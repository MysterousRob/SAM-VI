from Clippy_Personality import Personality


p = Personality("assets/pets/Clippy/personality.json")
p.say_random_idle()
p.say_for_mood("overheated")