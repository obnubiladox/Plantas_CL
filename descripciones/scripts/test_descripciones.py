"""Tests de descripciones.py: python -m unittest descripciones/scripts/test_descripciones.py"""
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import descripciones as d  # noqa: E402


def text(md):
    value, problems = d.convert(md)
    assert not problems, problems
    return value


class ConvertTest(unittest.TestCase):

    def test_full_example(self):
        md = (
            "# Vachellia caven\n\n"
            "## Morfología\n\n"
            "### Hojas\n"
            "Alternas, **bipinnadas**, con espinas. Semejante a *Vachellia\n"
            "farnesiana*.\n\n"
            "> Fuente: Rodríguez et al. 2018\n\n"
            "- Cáliz campanulado.\n"
            "* Corola _amarilla_.\n"
            "1) Uno\n"
        )
        self.assertEqual(
            "[[Morfología]]\n\n[{Hojas}]\n\n"
            "Alternas, **bipinnadas**, con espinas. Semejante a *Vachellia farnesiana*.\n\n"
            "{Fuente: Rodríguez et al. 2018}\n\n"
            "- Cáliz campanulado.\n- Corola *amarilla*.\n1. Uno",
            text(md),
        )

    def test_only_title_is_empty(self):
        self.assertEqual("", text("# Vachellia caven\n"))
        self.assertEqual("", text("﻿# Vachellia caven\r\n\r\n"))

    def test_paragraph_lines_and_hyphens_are_joined(self):
        self.assertEqual("Hojas bipinnadas, de 2-5 cm.", text("Hojas bipin-\nnadas,   de 2-5\ncm."))

    def test_list_item_continues_on_next_line(self):
        self.assertEqual("- Cáliz campanulado y\nverde.".replace("\n", " ").replace("- ", "- ", 1),
                         text("- Cáliz campanulado y\n  verde."))

    def test_quote_lines_join_in_one_source(self):
        self.assertEqual("Texto.\n\n{Fuente: Marticorena & Quezada 1985}", text("Texto.\n> Fuente: Marticorena\n> & Quezada 1985"))

    def test_emphasis(self):
        self.assertEqual("***las dos*** y **negrita *con cursiva***", text("***las dos*** y __negrita _con cursiva___"))
        self.assertEqual("snake_case y 2 \\* 3", text("snake_case y 2 * 3"))
        self.assertEqual("\\*sin cerrar", text("*sin cerrar"))
        self.assertEqual("un \\* y un \\\\", text("un \\* y un \\\\"))
        self.assertEqual("punto. y _guion", text("punto\\. y \\_guion"))

    def test_heading_with_closing_hashes(self):
        self.assertEqual("[[Morfología]]", text("## Morfología ##"))

    def test_problems(self):
        cases = {
            "Un `código`.": "código",
            "Ver <b>esto</b>.": "HTML",
            "Ver [aquí](https://x.cl).": "enlaces",
            "Ver https://x.cl": "direcciones",
            "Fuente {Autor 1985}": "llaves",
            "[[Título]]": "[[ ]]",
            "#### Cuatro": "dos niveles",
            "##Sin espacio": "espacio",
            "Texto\n\n---": "guiones",
            "| a | b |": "tablas",
            "    sangría": "sangría",
            "```\ncódigo\n```": "código",
            "Texto\n\n# Otro título": "primera línea",
            "&nbsp;": "entidades",
            "~~no~~": "tachado",
        }
        for md, word in cases.items():
            _, problems = d.convert(md)
            self.assertTrue(any(word in msg for _, msg in problems), f"{md!r}: {problems}")

    def test_problem_has_its_line(self):
        _, problems = d.convert("# X\n\nBien.\n\nMal `x`.")
        self.assertEqual([5], [line for line, _ in problems])


class NamesTest(unittest.TestCase):

    def test_from_especie(self):
        self.assertEqual("Asplenium obtusatum var. sphenoides",
                         d.from_especie("Asplenium obtusatum G. Forst. var. sphenoides (Kunze) C. Chr. ex Skottsb."))
        self.assertEqual("Adesmia emarginata var. x", d.from_especie("Adesmia emarginata Clos var. x Phil."))
        self.assertIsNone(d.from_especie("Adesmia"))

    def test_expected_name(self):
        self.assertEqual("12 Aa b_c.md", d.expected_name(d.Species(12, "Aa b/c", "F")))


class RenumberTest(unittest.TestCase):

    def test_renumbered_ficha_keeps_its_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fichas = root / "descripciones" / "Fichas"
            fichas.mkdir(parents=True)
            (fichas / "10 Aa bb.md").write_text("# Aa bb\n\nTexto escrito.\n", encoding="utf-8")
            (fichas / "20 Aa cc.md").write_text("# Aa cc\n", encoding="utf-8")          # plantilla vacía del N.° nuevo
            (fichas / "30 Dd ee.md").write_text("# Dd ee\n\nUno.\n", encoding="utf-8")
            (fichas / "40 Dd ff.md").write_text("# Dd ff\n\nDos.\n", encoding="utf-8")  # las dos con texto
            catalog = {20: d.Species(20, "Aa cc", "F"), 40: d.Species(40, "Dd ff", "F")}
            found = d.list_fichas(root, [])
            moved = d.move_renumbered(root, catalog, {10: 20, 30: 40}, found, in_git=False)
            self.assertEqual(1, moved)
            self.assertFalse((fichas / "10 Aa bb.md").exists())
            self.assertEqual("# Aa cc\n\nTexto escrito.\n", (fichas / "20 Aa cc.md").read_text("utf-8"))
            # Con texto en las dos no se toca nada: se junta a mano.
            self.assertTrue((fichas / "30 Dd ee.md").exists())
            self.assertEqual("# Dd ff\n\nDos.\n", (fichas / "40 Dd ff.md").read_text("utf-8"))


class ReleaseTest(unittest.TestCase):

    def test_hash_is_stable(self):
        # El mismo valor está en DescriptionPackageTest (app): las dos huellas tienen que coincidir.
        entries = {4534: ("descripciones/Fichas/4534 Vachellia caven.md", "Árbol **espinoso**."),
                   235: ("descripciones/Fichas/235 Asplenium gilliesii.md", None)}
        self.assertEqual("3f049ac8d3d900c3bb35a9f5d40542d8dcc42e05a2748ac4667089ca2a068dc8", d.content_hash(entries))
        self.assertEqual(d.content_hash(entries), d.content_hash(dict(reversed(list(entries.items())))))

    def test_changes_from_previous(self):
        old = {1: ("descripciones/Fichas/1 A a.md", "Uno."), 2: ("descripciones/Fichas/2 B b.md", None),
               3: ("descripciones/Fichas/3 C c.md", "Tres.")}
        new = {1: ("descripciones/Fichas/1 A a.md", "Uno cambiado."), 2: ("descripciones/Fichas/2 B b.md", None),
               4: ("descripciones/Fichas/4 D d.md", "Cuatro.")}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            m = d.build_release(out, new, 20261215, "2026-12-15",
                                [d.Previous(20261115, d.content_hash(old), old)], [{"name": "Ana", "login": "ana"}],
                                "", "https://x/releases/download/descripciones-20261215")
            self.assertEqual(2, m["rows"])
            self.assertEqual(3, m["species"])
            self.assertEqual(1, len(m["changes"]))
            change = json.loads(gzip.decompress((out / m["changes"][0]["url"].rsplit("/", 1)[1]).read_bytes()))
            self.assertEqual(d.content_hash(old), change["from"])
            self.assertEqual([1, 4], [e["id"] for e in change["entries"]])
            self.assertEqual([3], change["removed"])
            full = json.loads(gzip.decompress((out / "completo.json.gz").read_bytes()))
            self.assertIsNone(full["from"])
            self.assertNotIn("text", full["entries"][1])        # la ficha vacía va sin texto
            self.assertEqual(m["contentSha256"], full["contentSha256"])
            # Aplicar los cambios sobre la anterior da la nueva.
            applied = dict(old)
            for cid in change["removed"]:
                applied.pop(cid)
            for e in change["entries"]:
                applied[e["id"]] = (e["path"], e.get("text"))
            self.assertEqual(m["contentSha256"], d.content_hash(applied))

    def test_gzip_is_deterministic(self):
        self.assertEqual(d.gzip_bytes(b"hola"), d.gzip_bytes(b"hola"))


if __name__ == "__main__":
    unittest.main()
