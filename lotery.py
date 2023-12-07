import random

class LotrePlanet:
    def __init__(self):
        self.alien = ['Jupiter', 'Saturn', 'Uranus', 'Neptune']
        self.astronaut = ['Mercury', 'Venus', 'Earth', 'Mars']
        self.max_planets = 6
        self.astronaut_chance = 0.01
        self.alien_chance = 0.01
        self.alien_bonus = {'Jupiter': 45, 'Saturn': 25, 'Uranus': 15, 'Neptune': 10}
        self.astronaut_bonus = 5
        self.chosen_planets = {
            "Earth": 1000,
            "Saturn": 1000,
            "Uranus": 1000,
            "Neptune": 1000
        }

    def lotre(self):
        if len(self.chosen_planets) == 0:
            print("Anda belum memilih planet untuk melakukan lotre.")
            return

        result = random.choice(self.astronaut + self.alien)
        print("Planet yang keluar:", result)
        
        total_bonus = 0

        if (result in self.astronaut and random.random() < self.astronaut_chance) and result in self.chosen_planets:
            astronaut_bonus = sum(value for key, value in self.chosen_planets.items() if key in self.astronaut)
            return print(f"Selamat! Astronot keluar. Anda mendapatkan bonus {astronaut_bonus * self.astronaut_bonus} sebagai hasil taruhan pada planet astronot.")

        if (result in self.alien and random.random() < self.alien_chance) and result in self.chosen_planets:
            total_bonus = 0
            for planet, taruhan in self.chosen_planets.items():
                if planet in self.astronaut:
                    total_bonus += taruhan * self.astronaut_bonus
                elif planet in self.alien:
                    total_bonus += taruhan * self.alien_bonus[planet]
            return print(f"Selamat! Alien keluar. Anda mendapatkan bonus {total_bonus} sebagai hasil taruhan pada planet alien.")
            
        if result in self.chosen_planets:
            if result in self.astronaut:
                hasil = self.chosen_planets[result] * self.astronaut_bonus
                return print(f"Selamat! Planet {result} keluar. Anda mendapatkan {hasil} sebagai hasil taruhan.")
            else:
                hasil = self.chosen_planets[result] * self.alien_bonus[result]
                return print(f"Selamat! Planet {result} keluar. Anda mendapatkan {hasil} sebagai hasil taruhan.")

        if total_bonus == 0:
            return print("Tidak ada hasil pada planet yang keluar.")
        else:
            return print(f"Total bonus Anda adalah: {total_bonus}")

lotre = LotrePlanet()

lotre.lotre()