from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os
import io
from utils import db
from utils.track_generator import get_oval_position, get_horse_position, scale_and_translate_path
import json

HORSE_SIZE = (64, 64)
WIDTH, HEIGHT = 600, 400
FONT_PATH = "arial.ttf"  # Or any TTF file available
FONT_SIZE = 72

# Current file's directory
BOT_DIR = Path(__file__).resolve().parent.parent

# Go to sibling HorseRacingBotData/Data
DATA_PATH = BOT_DIR.parent / "HorseRacingBotData" / "Data"
ASSETS_PATH = BOT_DIR.parent / "HorseRacingBotData" / "Assets"



def generate_race_frame(horses, positions, track_img, track_length, track_points, horse_images):
    MARGIN = 80

    # Copy preloaded track image so we don't modify the original
    race_img = track_img.copy()

    for i, horse in enumerate(horses):
        progress = positions[horse["id"]] / track_length
        x, y = get_horse_position(track_points, progress)

        x = int(x)
        y = int(y)

        # Offset per horse so they don't overlap exactly
        y_offset = i * 10 - (len(horses) * 5)
        x_offset = i * 10 - (len(horses) * 5)

        img = horse_images[horse['id']]
        race_img.paste(
            img,
            (x + x_offset - HORSE_SIZE[0] // 2, y + y_offset - HORSE_SIZE[1] // 2),
            img
        )

    return race_img


def generate_race_gif(horses, positions_frames, track, track_length, duration=200):
    # Load static track image once
    track_img = load_track_image(track['id'], WIDTH, HEIGHT)

    # Load horse images once
    horse_images = {
        horse['id']: db.load_horse_image(horse['id'], HORSE_SIZE)
        for horse in horses
    }

    # Load track path points once
    with open(DATA_PATH / "tracks" / f"{track['id']}.json") as f:
        raw_path = json.load(f)

    track_points = [tuple(point) for point in raw_path[0]]
    scaled_track_points = track_points  # scaling disabled

    frames = []
    for positions in positions_frames:
        frame = generate_race_frame(horses, positions, track_img, track_length, scaled_track_points, horse_images)
        frames.append(frame.convert("P", palette=Image.ADAPTIVE))

    gif_bytes = io.BytesIO()
    frames[0].save(
        gif_bytes,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )
    gif_bytes.seek(0)

    size_bytes = len(gif_bytes.getvalue())
    print(f"GIF size: {size_bytes} bytes ({size_bytes / (1024 * 1024):.2f} MB)")

    return gif_bytes

def generate_slot_frames(grid):
    width, height = 300, 300  # size of the image
    image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Draw the 3x3 grid of emojis centered
    for r in range(3):
        for c in range(3):
            emoji = grid[r][c]
            x = c * 100 + 30
            y = r * 100 + 20
            draw.text((x, y), emoji, font=font, embedded_color=True)

    return image

def generate_slot_gif(frames_grids, duration=150):
    frames = [generate_slot_frames(grid) for grid in frames_grids]
    gif_bytes = io.BytesIO()
    frames[0].save(
        gif_bytes,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
        transparency=0,
    )
    gif_bytes.seek(0)
    return gif_bytes

def load_track_image(track_id, width, height):
    track_folder = Path(f'{ASSETS_PATH}/tracks')
    supported_exts = ['.png', '.jpg', '.jpeg', '.webp']  # add more if needed

    for ext in supported_exts:
        image_path = track_folder / f"{track_id}_image{ext}"
        if image_path.exists():
            return Image.open(image_path).convert("RGBA").resize((width, height))

    raise FileNotFoundError(f"No image found for track ID '{track_id}' with supported extensions.")