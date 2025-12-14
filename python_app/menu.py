import pygame
import os

def choose_pet(screen, font, pets_folder="assets/pets"):
    # detect pet folders (Cat, Cow, Dog, Pig)
    pet_folders = [
        f for f in os.listdir(pets_folder)
        if os.path.isdir(os.path.join(pets_folder, f))
    ]
    if not pet_folders:
        print("⚠️ No pet folders found in:", pets_folder)
        return None

    selected = 0
    clock = pygame.time.Clock()
    choosing = True

    while choosing:
        screen.fill((20, 20, 30))
        title = font.render("Choose your pet (↑ / ↓ then Enter)", True, (255, 255, 255))
        screen.blit(title, (50, 50))

        y = 150
        for i, pet_name in enumerate(pet_folders):
            color = (255, 255, 0) if i == selected else (180, 180, 180)
            text = font.render(pet_name, True, color)
            screen.blit(text, (100, y))
            y += 40

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                choosing = False
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(pet_folders)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(pet_folders)
                elif event.key == pygame.K_RETURN:
                    chosen_folder = pet_folders[selected]
                    chosen_path = os.path.join(pets_folder, chosen_folder)

                    # find .gif file inside selected folder
                    for file in os.listdir(chosen_path):
                        if file.lower().endswith(".gif"):
                            return os.path.join(chosen_path, file)

                    print(f"⚠️ No GIF found in {chosen_path}")
                    return None

        clock.tick(30)
