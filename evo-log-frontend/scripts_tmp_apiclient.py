import io, re

p = "src/lib/api-client.ts"
s = io.open(p, encoding="utf-8").read()
orig = s

# 1) incidentsAPI pointing at /api/incidents (no such route): drop the whole block.
lines = s.split("\n")
out = []
i = 0
while i < len(lines):
    if "Service Incidents (Ticketing)" in lines[i] and lines[i].lstrip().startswith("//"):
        i += 2  # comment + "export const incidentsAPI = {"
        while i < len(lines) and lines[i].strip() != "};":
            i += 1
        i += 1  # skip "};"
        continue
    out.append(lines[i])
    i += 1
s = "\n".join(out)

# 2) acconageAPI: declare the two lookups the /acconage screen needs.
s = s.replace(
    "  getAcconage: (id: number) => apiClient.get(`/api/v1/acconage/${id}`),",
    "  getAcconage: (id: number) => apiClient.get(`/api/v1/acconage/${id}`),\n"
    "  // Une operation d'acconage ne s'enregistre que sur une escale existante ;\n"
    "  // les listes alimentent le selecteur du formulaire (nom du navire via navires).\n"
    "  getEscales: (params?: Record<string, unknown>) => apiClient.get('/api/v1/acconage/escales', { params }),\n"
    "  getNavires: (params?: Record<string, unknown>) => apiClient.get('/api/v1/acconage/navires', { params }),",
)

# 3) Methods with no backend route and no caller = phantom promises.
for dead in ("deleteAcconage", "deleteMaintenance"):
    s = re.sub(r"[ \t]*%s: \([^\n]*\),\n" % dead, "", s)
s = re.sub(r",[ \t]*\n[ \t]*deleteTransit: \([^\n]*\)\n", "\n", s)

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("changed" if s != orig else "NO CHANGE", len(orig), "->", len(s))
