#!/usr/bin/env python3
"""Compares, utility by utility, two stylesheets in Tailwind's output format: the rules each
utility class produces (selector, at-rules around it, declarations) must be the same.

    tools/cssdiff.py reference.css generated.css [tokens.txt]

Used to check the style compiler against Tailwind CSS 4 on a real site's utilities."""
import re, sys

def blocks(s, i=0):
    """yields (prelude, body) of the blocks in s, and ('', decl) for declarations"""
    out = []
    n = len(s)
    buf = ""
    while i < n:
        c = s[i]
        if c == '"' or c == "'":
            j = s.index(c, i + 1)
            buf += s[i:j + 1]; i = j + 1; continue
        if c == "(":
            depth = 0; j = i
            while True:
                if s[j] == "(": depth += 1
                elif s[j] == ")":
                    depth -= 1
                    if depth == 0: break
                elif s[j] in "\"'":
                    j = s.index(s[j], j + 1)
                j += 1
            buf += s[i:j + 1]; i = j + 1; continue
        if c == "{":
            depth = 1; j = i + 1
            while depth:
                if s[j] == "{": depth += 1
                elif s[j] == "}": depth -= 1
                elif s[j] in "\"'": j = s.index(s[j], j + 1)
                j += 1
            out.append((buf.strip(), s[i + 1:j - 1])); buf = ""; i = j; continue
        if c == ";":
            if buf.strip(): out.append(("", buf.strip()))
            buf = ""; i += 1; continue
        if c == "}":
            i += 1; continue
        buf += c; i += 1
    if buf.strip(): out.append(("", buf.strip()))
    return out

def norm_decl(d):
    k, _, v = d.partition(":")
    return k.strip() + ":" + re.sub(r"\s+", " ", v.strip())

def canon_body(body):
    parts = []
    for pre, b in blocks(body):
        if not pre: parts.append(norm_decl(b))
        else: parts.append(re.sub(r"\s+", " ", pre) + "{" + canon_body(b) + "}")
    return ";".join(parts)

def rules(css):
    """(context, selector, canonical body) of every style rule, at any depth"""
    out = []
    def walk(s, ctx):
        for pre, b in blocks(s):
            if not pre: continue
            p = re.sub(r"\s+", " ", pre)
            if p.startswith("@layer"):
                walk(b, ctx)
            elif p.startswith("@media") or p.startswith("@supports") or p.startswith("@container"):
                walk(b, ctx + [p])
            elif p.startswith("@"):
                continue
            else:
                style_rule(p, b, ctx)
    def style_rule(sel, body, ctx):
        # declarations here, and the at-rules nested in the rule lifted around it: "a { x; @supports
        # (...) { y } }" is the same as "a { x } @supports (...) { a { y } }"
        decls = []
        for pre, b in blocks(body):
            if not pre:
                decls.append(norm_decl(b))
            else:
                style_rule(sel, b, ctx + [re.sub(r"\s+", " ", pre)])
        if decls:
            # "a, b { x }" is the same as "a { x } b { x }"
            for one in split_list(sel):
                out.append((tuple(ctx), one, ";".join(decls)))
    walk(css, [])
    return out

def split_list(sel):
    out, depth, start = [], 0, 0
    i = 0
    while i < len(sel):
        c = sel[i]
        if c == "\\": i += 2; continue
        if c in "([": depth += 1
        elif c in ")]": depth -= 1
        elif c == "," and depth == 0:
            out.append(sel[start:i].strip()); start = i + 1
        i += 1
    out.append(sel[start:].strip())
    return out

def unescape(s):
    return re.sub(r"\\(.)", r"\1", s)

def token_of(sel):
    m = re.search(r"\.((?:\\.|[A-Za-z0-9_-])+)", sel)
    return unescape(m.group(1)) if m else None

def by_token(css):
    d = {}
    for ctx, sel, body in rules(css):
        for part in [sel]:
            t = token_of(part)
            if t is None: continue
            d.setdefault(t, set()).add((ctx, sel, body))
    return d

if __name__ == "__main__":
    ref = by_token(open(sys.argv[1]).read())
    gen = by_token(open(sys.argv[2]).read())
    tokens = open(sys.argv[3]).read().split() if len(sys.argv) > 3 else sorted(ref)
    bad = 0
    for t in tokens:
        a, b = ref.get(t, set()), gen.get(t, set())
        if a == b: continue
        bad += 1
        print("✗", t)
        for x in sorted(a - b): print("   tailwind:", x)
        for x in sorted(b - a): print("   caju:    ", x)
    print(f"{len(tokens) - bad}/{len(tokens)} utilities match")
