#!/usr/bin/env python3
"""
JSP -> Angular modernization inventory.

Usage:
  python jsp_modernization_inventory.py --legacy /path/to/legacy-repo \
      --angular /path/to/angular-repo [--access-log access.log] [--out inventory.csv]

What it does:
  1. Finds every .jsp in the legacy repo, separating fragments/includes from real pages.
  2. Maps JSPs to entry points from Spring controllers (@RequestMapping/@GetMapping + returned
     view names) and Struts config (struts-config.xml / struts.xml forwards & results).
  3. Optionally counts hits per URL from an access log (Apache/Nginx common format).
  4. Extracts Angular routes (path + component) from *routing*.ts / files with Routes arrays.
  5. Fuzzy-joins legacy pages to Angular routes/components and writes a CSV you can finish by hand.

No third-party dependencies (stdlib only).
"""
import argparse, csv, difflib, os, re, sys
from collections import Counter, defaultdict

FRAGMENT_HINTS = ("include", "includes", "fragment", "fragments", "common", "layout", "tiles",
                  "template", "templates", "header", "footer", "taglib")

# ---------- helpers ----------
def norm(s):
    """Normalize a name for matching: lowercase, strip ext/paths/separators."""
    s = os.path.splitext(os.path.basename(s or ""))[0]
    s = re.sub(r"(component|page|view|action|controller)$", "", s, flags=re.I)
    return re.sub(r"[^a-z0-9]", "", s.lower())

def walk(root, exts):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("node_modules", "target", "build", "dist", ".git")]
        for f in fn:
            if f.lower().endswith(exts):
                yield os.path.join(dp, f)

def read(p):
    try:
        with open(p, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""

# ---------- legacy side ----------
def find_jsps(legacy):
    pages, fragments = [], []
    for p in walk(legacy, (".jsp", ".jspx", ".jspf")):
        rel = os.path.relpath(p, legacy).replace("\\", "/")
        parts = rel.lower().split("/")
        base = os.path.basename(rel).lower()
        is_frag = (rel.endswith(".jspf") or base.startswith("_")
                   or any(h in parts[:-1] for h in FRAGMENT_HINTS)
                   or any(base.startswith(h) for h in ("header", "footer", "nav", "menu")))
        (fragments if is_frag else pages).append(rel)
    return sorted(pages), sorted(fragments)

def spring_mappings(legacy):
    """Return {view_name_norm: [url,...]} from controllers."""
    out = defaultdict(set)
    for p in walk(legacy, (".java", ".kt")):
        src = read(p)
        if "Mapping(" not in src:
            continue
        class_prefix = ""
        m = re.search(r"@RequestMapping\s*\(\s*(?:value\s*=\s*)?\"([^\"]+)\"[^)]*\)\s*(?:public\s+)?class", src)
        if m:
            class_prefix = m.group(1)
        # each method mapping + the view names returned inside its body (approximate)
        for mm in re.finditer(
            r"@(?:Request|Get|Post|Put|Delete)Mapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?\{?\s*\"([^\"]+)\"",
            src):
            url = (class_prefix.rstrip("/") + "/" + mm.group(1).lstrip("/")).replace("//", "/")
            body = src[mm.end(): mm.end() + 2500]
            views = re.findall(r"return\s+\"([^\"]+)\"", body)
            views += re.findall(r"ModelAndView\s*\(\s*\"([^\"]+)\"", body)
            for v in views:
                if v.startswith("redirect:") or v.startswith("forward:"):
                    continue
                out[norm(v)].add(url)
    return out

def struts_mappings(legacy):
    """Return {jsp_norm: [action_path,...]} from struts-config.xml / struts.xml."""
    out = defaultdict(set)
    for p in walk(legacy, (".xml",)):
        if "struts" not in os.path.basename(p).lower():
            continue
        src = read(p)
        # Struts 1: <action path="/foo" ...> <forward name="x" path="/WEB-INF/jsp/foo.jsp"/>
        for a in re.finditer(r"<action\s+[^>]*path=\"([^\"]+)\"[^>]*>(.*?)</action>", src, re.S):
            for jsp in re.findall(r"path=\"([^\"]+\.jspx?)\"", a.group(2)):
                out[norm(jsp)].add(a.group(1))
        # Struts 2: <action name="foo"><result>/foo.jsp</result></action>
        for a in re.finditer(r"<action\s+[^>]*name=\"([^\"]+)\"[^>]*>(.*?)</action>", src, re.S):
            for jsp in re.findall(r">\s*([^<\s]+\.jspx?)\s*<", a.group(2)):
                out[norm(jsp)].add("/" + a.group(1))
    return out

def access_log_hits(path):
    hits = Counter()
    if not path:
        return hits
    for line in read(path).splitlines():
        m = re.search(r"\"(?:GET|POST)\s+([^\s?\"]+)", line)
        if m:
            hits[m.group(1)] += 1
    return hits

# ---------- angular side ----------
def angular_routes(angular):
    """Return list of (path, component, file)."""
    routes = []
    for p in walk(angular, (".ts",)):
        if p.endswith(".spec.ts"):
            continue
        src = read(p)
        if "Routes" not in src and "loadChildren" not in src and "path:" not in src:
            continue
        for m in re.finditer(r"\{\s*path\s*:\s*['\"]([^'\"]*)['\"]\s*,([^{}]*)", src):
            body = m.group(2)
            comp = re.search(r"component\s*:\s*(\w+)", body)
            lazy = re.search(r"loadChildren|loadComponent", body)
            routes.append((m.group(1), comp.group(1) if comp else ("<lazy>" if lazy else ""),
                           os.path.relpath(p, angular)))
    return routes

def angular_components(angular):
    comps = {}
    for p in walk(angular, (".component.ts",)):
        src = read(p)
        m = re.search(r"export\s+class\s+(\w+)", src)
        if m:
            comps[m.group(1)] = os.path.relpath(p, angular)
    return comps

# ---------- join ----------
def best_match(key, candidates, cutoff=0.72):
    if not key or not candidates:
        return None, 0.0
    res = difflib.get_close_matches(key, candidates.keys(), n=1, cutoff=cutoff)
    if res:
        return candidates[res[0]], difflib.SequenceMatcher(None, key, res[0]).ratio()
    return None, 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy", required=True)
    ap.add_argument("--angular", required=True)
    ap.add_argument("--access-log")
    ap.add_argument("--out", default="inventory.csv")
    a = ap.parse_args()

    pages, fragments = find_jsps(a.legacy)
    spring = spring_mappings(a.legacy)
    struts = struts_mappings(a.legacy)
    hits = access_log_hits(a.access_log)
    routes = angular_routes(a.angular)
    comps = angular_components(a.angular)

    # candidate index: normalized route path segment & component name -> (route, component)
    cand = {}
    for path, comp, f in routes:
        if path in ("", "**"):
            continue
        cand[norm(path.split("/")[-1])] = (path, comp)
        if comp and comp != "<lazy>":
            cand[norm(comp)] = (path, comp)
    for comp in comps:                       # components not yet routed still count as "in progress"
        cand.setdefault(norm(comp), ("", comp))

    rows, status_count = [], Counter()
    for jsp in pages:
        key = norm(jsp)
        urls = sorted(spring.get(key, set()) | struts.get(key, set()))
        traffic = sum(hits.get(u, 0) for u in urls) if hits else ""
        match, score = best_match(key, cand)
        ng_path, ng_comp = match if match else ("", "")
        if match and ng_path:
            status = "Done (verify)"
        elif match:
            status = "In progress (component, no route)"
        elif hits and not traffic:
            status = "Candidate to retire (no traffic)"
        else:
            status = "Not started"
        status_count[status] += 1
        rows.append({"jsp": jsp, "legacy_urls": " | ".join(urls), "traffic_hits": traffic,
                     "angular_route": ng_path, "angular_component": ng_comp,
                     "match_confidence": f"{score:.2f}" if match else "",
                     "status": status, "backend_api_ready": "", "notes": ""})

    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["jsp"])
        w.writeheader(); w.writerows(rows)

    # unmatched Angular routes -> may be new pages or consolidations
    matched_comps = {r["angular_component"] for r in rows}
    extra = [(p, c) for p, c, _ in routes if c and c not in matched_comps and p not in ("", "**")]

    print(f"\nLegacy JSP pages: {len(pages)}   fragments/includes skipped: {len(fragments)}")
    print(f"Angular routes: {len(routes)}   components: {len(comps)}")
    for s, n in status_count.most_common():
        print(f"  {s:<40} {n}")
    if extra:
        print(f"\nAngular routes with no legacy match ({len(extra)}) — new pages or consolidations:")
        for p, c in extra[:30]:
            print(f"  /{p}  ->  {c}")
    print(f"\nWrote {a.out}. Review 'Done (verify)' rows with confidence < 0.9 by hand.")

if __name__ == "__main__":
    main()
