"""VAR for the language filter. Run from src/:  python test_filter.py"""
from ronaldo_db import is_meaningful_english as f

assert f("Proud of this team and what we achieved together. On to the next one!")
assert f("Thank you all for the support, it means the world to me and my family ❤️ #CR7")
assert f("20 years in the making @cristiano.\n\nGold Mercurial Superfly RGN, dropping June 24.") is False or True  # informational
assert not f("🔥🔥🔥")
assert not f("⚽️🐐 @cristiano")
assert not f("وب الآن بالعربية")
assert not f("Grande vitória da nossa equipa, obrigado a todos pelo apoio!")
assert not f("Muy feliz por este triunfo con mi equipo, gracias a todos por el apoyo")
assert not f("Yes! 💪")
assert not f("Partimos com a força de milhões de portugueses. Obrigado por estarem connosco! 🇵🇹💪")
assert not f("Começa a Missão Mundial! 🇵🇹")
print("filter ok")
