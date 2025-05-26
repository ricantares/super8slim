
from lotteria import Lotteria
"""
    Unit test lotteria 

    run: pytest -q /home/rromiti/super8/sw/test_lotteria.py
"""
class TestLotteria:

    # prova test ok
    def test_combinazioni_caricamento_ok(self):
        file_estrazione = "/home/rromiti/super8/sw/data/estrazioni_test_90.csv"
        ll = Lotteria(file_estrazione)
        assert ll.elementi_storico == 90

    # prova test ok
    def test_combinazioni_genera(self):
        ll = Lotteria()
        assert len(ll.genera_estrazione()) == 6

    # prova test ko
    def test_combinazioni_caricamento_ko(self):
        file_estrazione = "/home/rromiti/super8/sw/data/estrazioni_test_90.csv"
        ll = Lotteria(file_estrazione)
        assert ll.elementi_storico != 90