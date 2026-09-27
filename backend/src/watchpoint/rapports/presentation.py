"""La presentation — le panorama, mais montrable a quelqu'un.

    cd ~/Desktop/WP
    python -m watchpoint rapport presentation

Meme matiere que rapports/panorama.py, autre usage : celui-ci sort une page HTML
autonome, datee, qui va dans docs/livrables/documents/. Le markdown est pour travailler,
celui-ci est pour montrer.

Rien n'y est ecrit a la main. Si un chiffre bouge dans la base, il bouge ici a
la prochaine execution — c'est la seule facon de ne jamais presenter un chiffre
perime.
"""
from __future__ import annotations

from watchpoint import config

import collections
import datetime as dt
import html
import json
import pathlib
import sys


from watchpoint import sources  # noqa: E402

LABO = config.RACINE
DATA = LABO / "data"
CUMUL = DATA / "price_points.jsonl"
SORTIE = config.LIVRABLES / "documents"

NATURES = {"realised": "réalisé", "sold": "vendu", "asking": "demandé",
           "estimate": "estimation", "msrp": "prix neuf"}
TYPES = {"auction": "maison de ventes", "dealer": "marchand",
         "marketplace": "marketplace", "community": "forums",
         "aggregator": "agrégateur"}
VERDICTS = {"GARDER": "gardé", "REJETER": "rejeté", "QUARANTAINE": "quarantaine"}


def milliers(n) -> str:
    return f"{n:,}".replace(",", " ")


def e(texte) -> str:
    return html.escape(str(texte))


def lire() -> tuple[dict, dict]:
    par_source = collections.defaultdict(lambda: {
        "prix": 0, "natures": collections.Counter(), "verdicts": collections.Counter(),
        "regles": collections.Counter(), "reference": 0,
        "provenance_reference": collections.Counter(),
        "provenance_nature": collections.Counter(),
        "devises": collections.Counter(), "annees": collections.Counter(), "marque": 0,
    })
    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            s = par_source[r["source_id"]]
            s["prix"] += 1
            s["natures"][r.get("price_nature")] += 1
            s["verdicts"][r.get("filter_verdict") or "?"] += 1
            if r.get("filter_verdict") != "GARDER":
                s["regles"][f"{r.get('filter_verdict')} {r.get('filter_rule')}"] += 1
            if r.get("reference"):
                s["reference"] += 1
                s["provenance_reference"][r.get("reference_provenance") or "?"] += 1
                # Un SKU de marchand n'est pas une reference constructeur : les
                # confondre fait lire 100 % la ou il n'y a rien d'exploitable.
                if r.get("reference_provenance") in ("champ_dedie", "extrait_titre",
                                                 "extrait_description"):
                    s["reference_sure"] = s.get("reference_sure", 0) + 1
            s["provenance_nature"][r.get("price_nature_provenance") or "non renseignée"] += 1
            if r.get("brand"):
                s["marque"] += 1
            if r.get("price_currency"):
                s["devises"][r["price_currency"]] += 1
            if r.get("price_date"):
                s["annees"][str(r["price_date"])[:4]] += 1

    brut = {}
    racine = DATA / "raw"
    if racine.exists():
        for dossier in racine.iterdir():
            fichiers = [*dossier.glob("*.json"), *dossier.glob("*.json.gz")] if dossier.is_dir() else []
            if fichiers:
                brut[dossier.name] = {
                    "collectes": len(fichiers),
                    "mo": sum(f.stat().st_size for f in fichiers) / 1_048_576,
                }
    return par_source, brut


def barre(verdicts: collections.Counter, total: int) -> str:
    """La barre empilee : gardé, rejeté, quarantaine. L'information est la forme."""
    if not total:
        return ""
    segments = []
    for cle, classe in (("GARDER", "garde"), ("REJETER", "rejet"),
                        ("QUARANTAINE", "quarantaine")):
        part = verdicts.get(cle, 0)
        if part:
            segments.append(
                f'<span class="seg seg--{classe}" style="flex:{part}" '
                f'title="{VERDICTS[cle]} {milliers(part)}"></span>')
    return f'<span class="barre">{"".join(segments)}</span>'


def page(par_source, brut) -> str:
    metas = {m.SOURCE["id"]: m.SOURCE for m in sources.ALL}
    actives = {s: d for s, d in par_source.items() if d["prix"]}
    total = sum(d["prix"] for d in actives.values())
    garde = sum(d["verdicts"].get("GARDER", 0) for d in actives.values())
    rejet = sum(d["verdicts"].get("REJETER", 0) for d in actives.values())
    quarantaine = sum(d["verdicts"].get("QUARANTAINE", 0) for d in actives.values())
    reference = sum(d["reference"] for d in actives.values())
    reference_sure = sum(d.get("reference_sure", 0) for d in actives.values())
    mo = sum(b["mo"] for b in brut.values())
    collectes = sum(b["collectes"] for b in brut.values())

    annees = collections.Counter()
    natures = collections.Counter()
    devises = collections.Counter()
    regles = collections.Counter()
    for d in actives.values():
        annees.update(d["annees"])
        natures.update(d["natures"])
        devises.update(d["devises"])
        regles.update(d["regles"])
    annees_utiles = {a: n for a, n in annees.items() if a.isdigit() and int(a) >= 2005}
    pic = max(annees_utiles.values(), default=1)

    ordre = sorted(actives.items(), key=lambda kv: -kv[1]["prix"])

    # -- les chiffres de tete
    tuiles = [
        (milliers(total), "prix collectés", f"{len(actives)} sources actives"),
        (milliers(garde), "gardés par le filtre",
         f"{round(100 * garde / max(total, 1))} % du collecté"),
        (f"{min(annees_utiles, default='—')} → {max(annees_utiles, default='—')}",
         "profondeur historique", "date de vente ou de mise en ligne"),
        (f"{mo:.0f} Mo", "de brut conservé",
         f"{collectes} collectes rejouables hors ligne"),
    ]

    # -- sources
    lignes_sources = []
    for sid, d in ordre:
        meta = metas.get(sid, {})
        b = brut.get(sid, {})
        nature = max(d["natures"], key=d["natures"].get)
        lignes_sources.append(f"""
        <tr>
          <th scope="row"><span class="nom">{e(meta.get('name', sid))}</span>
            <span class="type">{e(TYPES.get(meta.get('type'), meta.get('type', '')))}</span></th>
          <td class="num">{milliers(d['prix'])}</td>
          <td><span class="pastille pastille--{nature}">{e(NATURES.get(nature, nature))}</span></td>
          <td class="num">{min(d['annees'], default='—')} → {max(d['annees'], default='—')}</td>
          <td class="num">{d.get('reference_sure', 0) * 100 // max(d['prix'], 1)} %</td>
          <td class="bar">{barre(d['verdicts'], d['prix'])}</td>
          <td class="num">{b.get('mo', 0):.1f} Mo</td>
        </tr>""")

    muettes = [(m.SOURCE["id"], m.SOURCE) for m in sources.ALL
               if m.SOURCE["id"] not in actives]
    lignes_muettes = "".join(
        f"<li><b>{e(meta.get('name', sid))}</b> — "
        f"{e(meta.get('statut') or 'adaptateur écrit, collecte pas encore aboutie')}</li>"
        for sid, meta in muettes)

    # -- natures
    lignes_natures = []
    for n, c in natures.most_common():
        lignes_natures.append(f"""
        <tr><th scope="row"><span class="pastille pastille--{n}">{e(NATURES.get(n, n))}</span></th>
          <td class="num">{milliers(c)}</td>
          <td class="bar"><span class="barre"><span class="seg seg--{n}"
            style="flex:{c}"></span><span class="seg seg--vide"
            style="flex:{max(total - c, 0)}"></span></span></td>
          <td class="num">{round(100 * c / max(total, 1))} %</td></tr>""")

    # -- reference
    lignes_ref = []
    for sid, d in ordre:
        prov = " · ".join(f"{p} {milliers(c)}"
                          for p, c in d["provenance_reference"].most_common()) or "aucune"
        lignes_ref.append(f"""
        <tr><th scope="row">{e(metas.get(sid, {}).get('name', sid))}</th>
          <td class="num">{d.get('reference_sure', 0) * 100 // max(d['prix'], 1)} %</td>
          <td class="num">{d['marque'] * 100 // max(d['prix'], 1)} %</td>
          <td class="prov">{e(prov)}</td></tr>""")

    # -- profondeur
    lignes_annees = []
    for annee in sorted(annees_utiles, reverse=True):
        n = annees_utiles[annee]
        principale = max(
            ((metas.get(s, {}).get("name", s), d["annees"][annee])
             for s, d in actives.items() if d["annees"].get(annee)),
            key=lambda kv: kv[1], default=("—", 0))[0]
        lignes_annees.append(f"""
        <tr><th scope="row">{annee}</th>
          <td class="num">{milliers(n)}</td>
          <td class="bar"><span class="barre"><span class="seg seg--accent"
            style="flex:{n}"></span><span class="seg seg--vide"
            style="flex:{max(pic - n, 1)}"></span></span></td>
          <td class="prov">{e(principale)}</td></tr>""")

    # -- reserves
    reserves = [(metas[s].get("name", s), metas[s]["reserve"])
                for s, _ in ordre if metas.get(s, {}).get("reserve")]
    lignes_reserves = "".join(
        f"<li><b>{e(nom)}</b> — {e(texte)}</li>" for nom, texte in reserves)

    lignes_regles = "".join(
        f'<tr><th scope="row"><code>{e(regle)}</code></th>'
        f'<td class="num">{milliers(n)}</td></tr>'
        for regle, n in regles.most_common(8))

    lignes_devises = "".join(
        f'<tr><th scope="row">{e(d)}</th><td class="num">{milliers(c)}</td></tr>'
        for d, c in devises.most_common())

    aujourdhui = dt.date.today()
    return f"""<title>Panorama des sources Watchpoint</title>
<style>
  :root {{
    --ground:#F2F5F2; --surface:#FFFFFF; --ink:#12171A; --muted:#5C686B;
    --rule:#DCE3DE; --accent:#0E6B5B; --garde:#0E6B5B; --rejet:#96382C;
    --quarantaine:#9A7418; --vide:#E3E8E4;
    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans: system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --ground:#0D1012; --surface:#161A1C; --ink:#E6EAE8; --muted:#98A3A6;
      --rule:#252B2D; --accent:#4EBFA7; --garde:#4EBFA7; --rejet:#D2705E;
      --quarantaine:#CB9F3E; --vide:#1F2426;
    }}
  }}
  :root[data-theme="dark"] {{
    --ground:#0D1012; --surface:#161A1C; --ink:#E6EAE8; --muted:#98A3A6;
    --rule:#252B2D; --accent:#4EBFA7; --garde:#4EBFA7; --rejet:#D2705E;
    --quarantaine:#CB9F3E; --vide:#1F2426;
  }}
  * {{ box-sizing:border-box; }}
  body {{
    margin:0; background:var(--ground); color:var(--ink);
    font-family:var(--sans); font-size:16px; line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }}
  .page {{ max-width:1060px; margin:0 auto; padding:clamp(28px,5vw,72px) clamp(18px,4vw,40px) 80px; }}
  header {{ border-bottom:2px solid var(--ink); padding-bottom:28px; margin-bottom:44px; }}
  .eyebrow {{
    font-family:var(--mono); font-size:11px; letter-spacing:.14em;
    text-transform:uppercase; color:var(--muted); margin:0 0 14px;
  }}
  h1 {{
    font-family:var(--serif); font-weight:600; font-size:clamp(34px,5.2vw,54px);
    line-height:1.08; margin:0 0 14px; text-wrap:balance; letter-spacing:-.01em;
  }}
  .chapeau {{ max-width:62ch; color:var(--muted); margin:0; font-size:17px; }}
  section {{ margin:0 0 56px; }}
  h2 {{
    font-family:var(--serif); font-size:clamp(21px,2.6vw,27px); font-weight:600;
    margin:0 0 6px; letter-spacing:-.01em;
  }}
  h2 + p {{ margin:0 0 20px; color:var(--muted); max-width:66ch; }}
  .tuiles {{ display:grid; gap:1px; background:var(--rule); border:1px solid var(--rule);
    grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); margin-bottom:52px; }}
  .tuile {{ background:var(--surface); padding:20px 22px 22px; }}
  .tuile b {{ display:block; font-family:var(--mono); font-size:clamp(24px,3.4vw,32px);
    font-weight:600; letter-spacing:-.02em; font-variant-numeric:tabular-nums; }}
  .tuile span {{ display:block; font-size:14px; margin-top:4px; }}
  .tuile em {{ display:block; font-style:normal; font-size:12.5px; color:var(--muted); margin-top:2px; }}
  .table-wrap {{ overflow-x:auto; border:1px solid var(--rule); background:var(--surface); }}
  table {{ border-collapse:collapse; width:100%; font-size:14.5px; }}
  caption {{ text-align:left; padding:14px 18px 0; color:var(--muted); font-size:13px; }}
  th, td {{ padding:11px 14px; text-align:left; border-bottom:1px solid var(--rule); vertical-align:middle; }}
  thead th {{
    font-family:var(--mono); font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
    color:var(--muted); font-weight:500; border-bottom:1px solid var(--ink);
  }}
  tbody tr:last-child th, tbody tr:last-child td {{ border-bottom:none; }}
  tbody th {{ font-weight:600; }}
  .num {{ font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap; }}
  .nom {{ display:block; }}
  .type {{ display:block; font-size:12px; color:var(--muted); font-weight:400; }}
  .prov {{ font-size:13px; color:var(--muted); }}
  .bar {{ width:180px; min-width:140px; }}
  .barre {{ display:flex; height:9px; width:100%; overflow:hidden; }}
  .seg {{ display:block; }}
  .seg--garde, .seg--realised {{ background:var(--garde); }}
  .seg--rejet {{ background:var(--rejet); }}
  .seg--quarantaine {{ background:var(--quarantaine); }}
  .seg--accent, .seg--sold {{ background:var(--accent); }}
  .seg--asking {{ background:var(--quarantaine); }}
  .seg--estimate {{ background:var(--muted); }}
  .seg--vide {{ background:var(--vide); }}
  .pastille {{
    font-family:var(--mono); font-size:11px; letter-spacing:.06em; text-transform:uppercase;
    padding:3px 8px; border:1px solid currentColor; white-space:nowrap;
  }}
  .pastille--realised {{ color:var(--garde); }}
  .pastille--sold {{ color:var(--accent); }}
  .pastille--asking {{ color:var(--quarantaine); }}
  .legende {{ display:flex; flex-wrap:wrap; gap:18px; margin:14px 0 0;
    font-family:var(--mono); font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }}
  .legende i {{ display:inline-block; width:11px; height:11px; margin-right:6px; vertical-align:-1px; font-style:normal; }}
  ul.notes {{ margin:16px 0 0; padding:0; list-style:none; }}
  ul.notes li {{ padding:11px 0 11px 18px; border-top:1px solid var(--rule);
    position:relative; font-size:14.5px; color:var(--muted); }}
  ul.notes li::before {{ content:""; position:absolute; left:0; top:19px;
    width:7px; height:1px; background:var(--muted); }}
  ul.notes b {{ color:var(--ink); }}
  code {{ font-family:var(--mono); font-size:12.5px; }}
  .grille-2 {{ display:grid; gap:26px; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); }}
  footer {{ border-top:1px solid var(--rule); padding-top:20px; color:var(--muted); font-size:13px; }}
  footer code {{ color:var(--ink); }}
</style>

<div class="page">
<header>
  <p class="eyebrow">Watchpoint · état des données · {aujourdhui.strftime('%d.%m.%Y')}</p>
  <h1>Ce que nous avons collecté,<br>et ce qui en est exploitable</h1>
  <p class="chapeau">{milliers(total)} prix ramenés de {len(actives)} sources, chacun
  daté, chiffré dans sa devise d'origine et porteur de sa nature. Le filtre a tranché
  ligne par ligne à l'entrée&nbsp;: rien n'a été supprimé, tout a été marqué.</p>
</header>

<div class="tuiles">
  {''.join(f'<div class="tuile"><b>{v}</b><span>{l}</span><em>{s}</em></div>'
           for v, l, s in tuiles)}
</div>

<section>
  <h2>Les sources</h2>
  <p>Chaque source apporte une nature de prix et une profondeur différentes. La barre
  montre ce que le filtre fait de sa récolte.</p>
  <div class="table-wrap">
    <table>
      <thead><tr>
        <th scope="col">Source</th><th scope="col">Prix</th><th scope="col">Nature dominante</th>
        <th scope="col">Période</th><th scope="col">Réf. constructeur</th>
        <th scope="col">Filtre</th><th scope="col">Brut</th>
      </tr></thead>
      <tbody>{''.join(lignes_sources)}</tbody>
    </table>
  </div>
  <p class="legende">
    <span><i style="background:var(--garde)"></i>gardé</span>
    <span><i style="background:var(--rejet)"></i>rejeté</span>
    <span><i style="background:var(--quarantaine)"></i>quarantaine</span>
  </p>
  <ul class="notes">{lignes_muettes}</ul>
</section>

<section>
  <h2>Les natures de prix</h2>
  <p>C'est la question qui décide de ce qu'on peut afficher. Un prix demandé est une
  opinion de vendeur&nbsp;; un prix réalisé est une transaction.</p>
  <div class="table-wrap">
    <table><thead><tr>
      <th scope="col">Nature</th><th scope="col">Prix</th><th scope="col"></th><th scope="col">Part</th>
    </tr></thead><tbody>{''.join(lignes_natures)}</tbody></table>
  </div>
</section>

<section class="grille-2">
  <div>
    <h2>Ce que le filtre écarte</h2>
    <p>Et pour quelle raison exactement.</p>
    <div class="table-wrap">
      <table><thead><tr><th scope="col">Verdict et règle</th><th scope="col">Lignes</th></tr></thead>
      <tbody>{lignes_regles}</tbody></table>
    </div>
  </div>
  <div>
    <h2>Les devises</h2>
    <p>Aucune conversion n'est appliquée. Ne jamais comparer deux lignes de devises
    différentes.</p>
    <div class="table-wrap">
      <table><thead><tr><th scope="col">Devise</th><th scope="col">Prix</th></tr></thead>
      <tbody>{lignes_devises}</tbody></table>
    </div>
  </div>
</section>

<section>
  <h2>La référence</h2>
  <p>Elle n'est pas un critère de filtrage&nbsp;: un prix sans référence reste une
  observation de marché valide. Elle est le crochet d'identité entre une annonce et une
  montre — sans elle, on a un prix mais pas de quoi.
  <b>{milliers(reference)} prix sur {milliers(total)} portent un identifiant, mais
  seulement {milliers(reference_sure)} portent une vraie référence constructeur.</b>
  La différence n'est pas cosmétique : un SKU est un numéro d'inventaire de
  marchand, et une référence lue dans le corps d'une annonce peut être un calibre
  ou un numéro de boîtier.</p>
  <div class="table-wrap">
    <table><thead><tr>
      <th scope="col">Source</th><th scope="col">Un identifiant</th>
      <th scope="col">Dont réf. constructeur</th>
      <th scope="col">Avec marque</th><th scope="col">D'où il vient</th>
    </tr></thead><tbody>{''.join(lignes_ref)}</tbody></table>
  </div>
</section>

<section>
  <h2>La profondeur historique</h2>
  <p>Attention à ce que la date signifie&nbsp;: chez une maison de ventes c'est le jour
  du marteau, chez un marchand c'est la mise en ligne de l'annonce. La seconde ne date
  pas une transaction.</p>
  <div class="table-wrap">
    <table><thead><tr>
      <th scope="col">Année</th><th scope="col">Prix</th><th scope="col"></th>
      <th scope="col">Source principale</th>
    </tr></thead><tbody>{''.join(lignes_annees)}</tbody></table>
  </div>
</section>

<section>
  <h2>Les réserves connues</h2>
  <p>Ce que chaque source ne peut pas dire, ou dit mal. À lire avant toute analyse qui
  s'appuie sur elle.</p>
  <ul class="notes">
    {lignes_reserves}
    <li><b>Christie's publie ses prix frais acheteur inclus</b>, Artcurial et Lyon &amp;
    Turnbull le marteau nu — environ un quart d'écart. Le champ
    <code>price_includes_premium</code> porte l'information ligne par ligne&nbsp;;
    toute comparaison entre maisons qui l'ignore surévalue Christie's.</li>
    <li><b>Les invendus sont invisibles</b> chez les maisons de ventes qui ne servent que
    leurs lots vendus&nbsp;: toute moyenne héritera d'un biais de survie.</li>
    <li><b>La date d'un marchand est celle de la mise en ligne</b>, pas celle de la vente.
    Une montre publiée en 2016 et vendue en 2019 porte 2016.</li>
    <li><b>La quarantaine n'est pas un déchet</b>&nbsp;: {milliers(quarantaine)} lignes que
    le texte seul ne permet pas de trancher, à échantillonner chaque semaine pour mesurer
    le taux d'erreur réel.</li>
  </ul>
</section>

<footer>
  Document généré le {aujourdhui.isoformat()} par <code>rapports/presentation.py</code>.
  Aucun chiffre n'y est écrit à la main&nbsp;: il est régénéré à chaque collecte.
  Détail complet dans <code>docs/rapports/PANORAMA.md</code> et <code>docs/rapports/ETAT_CHAMPS.md</code>.
</footer>
</div>
"""


def main() -> None:
    par_source, brut = lire()
    SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = SORTIE / f"PANORAMA_sources_{dt.date.today().isoformat()}.html"
    chemin.write_text(page(par_source, brut), encoding="utf-8")
    print(f"-> {chemin}")


if __name__ == "__main__":
    main()
