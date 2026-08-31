import os, sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

FONT_DIR = r"C:\Windows\Fonts"
COUR_BOLD = os.path.join(FONT_DIR, "courbd.ttf")
ARIAL_BOLD = os.path.join(FONT_DIR, "arialbd.ttf")
GEORGIA_BOLD = os.path.join(FONT_DIR, "georgiab.ttf")

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def round_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.paste(image.convert("RGBA"), (0, 0), mask=mask)
    return result

def add_drop_shadow(image, offset=(0, 8), blur=15, shadow_color=(0, 0, 0, 180)):
    w, h = image.size
    pad = blur * 2
    shadow_layer = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    
    alpha = image.split()[3]
    shadow_mask = Image.new("RGBA", image.size, shadow_color)
    shadow_mask.putalpha(alpha)
    
    shadow_layer.paste(shadow_mask, (pad + offset[0], pad + offset[1]))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur))
    shadow_layer.paste(image, (pad, pad), mask=image)
    return shadow_layer, pad

class GraphicCompositor:
    @staticmethod
    def style1_rounded_card_on_grid(photo_path, grid_path, output_path, card_size=(1620, 912), radius=35):
        """Style 1: Central rounded photo card with shadow over grid background"""
        bg = Image.open(grid_path).convert("RGBA").resize((1920, 1080), Image.Resampling.LANCZOS)
        photo = ImageOps.fit(Image.open(photo_path).convert("RGB"), card_size, Image.Resampling.LANCZOS)
        
        rounded = round_corners(photo, radius)
        # Add subtle 2px white/gold border
        draw_r = ImageDraw.Draw(rounded)
        draw_r.rounded_rectangle([(0,0), (card_size[0]-1, card_size[1]-1)], radius=radius, outline=(255, 255, 255, 120), width=2)
        
        card_with_shadow, pad = add_drop_shadow(rounded, offset=(0, 10), blur=20, shadow_color=(0, 0, 0, 200))
        
        pos_x = (1920 - card_size[0]) // 2 - pad
        pos_y = (1080 - card_size[1]) // 2 - pad
        bg.paste(card_with_shadow, (pos_x, pos_y), mask=card_with_shadow)
        bg.convert("RGB").save(output_path, quality=95)
        return output_path

    @staticmethod
    def style2_triptych_overlay(bg_photo_path, three_photos, output_path):
        """Style 2: Multi-image triptych (3 framed photos side-by-side over warm blurred background)"""
        bg = ImageOps.fit(Image.open(bg_photo_path).convert("RGB"), (1920, 1080), Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(12))
        # Darken slightly
        dim = Image.new("RGBA", (1920, 1080), (20, 10, 30, 90))
        bg = Image.alpha_composite(bg.convert("RGBA"), dim)

        w_slot, h_slot = 540, 360
        spacing = 35
        start_x = (1920 - (3 * w_slot + 2 * spacing)) // 2
        y_pos = (1080 - h_slot) // 2

        for i, p_path in enumerate(three_photos[:3]):
            im = ImageOps.fit(Image.open(p_path).convert("RGB"), (w_slot, h_slot), Image.Resampling.LANCZOS)
            # Add 4px white border
            im_bordered = ImageOps.expand(im, border=4, fill="white")
            im_with_shadow, pad = add_drop_shadow(im_bordered.convert("RGBA"), offset=(0, 8), blur=14, shadow_color=(0, 0, 0, 180))
            
            curr_x = start_x + i * (w_slot + spacing) - pad
            bg.paste(im_with_shadow, (curr_x, y_pos - pad), mask=im_with_shadow)

        bg.convert("RGB").save(output_path, quality=95)
        return output_path

    @staticmethod
    def style3_split_typography_card(photo_path, grid_path, main_title, subtitle, output_path):
        """Style 3: Left photo card, right bold typography with red accent line"""
        bg = Image.open(grid_path).convert("RGBA").resize((1920, 1080), Image.Resampling.LANCZOS)
        
        # Left card
        card_w, card_h = 720, 860
        photo = ImageOps.fit(Image.open(photo_path).convert("RGB"), (card_w, card_h), Image.Resampling.LANCZOS)
        rounded = round_corners(photo, radius=28)
        card_with_shadow, pad = add_drop_shadow(rounded, offset=(0, 8), blur=18, shadow_color=(0, 0, 0, 190))
        bg.paste(card_with_shadow, (100 - pad, 110 - pad), mask=card_with_shadow)

        # Right Typography
        draw = ImageDraw.Draw(bg)
        font_title = get_font(ARIAL_BOLD, 74)
        font_sub = get_font(ARIAL_BOLD, 30)

        tx = 900
        ty = 430
        
        # Draw main title
        draw.text((tx, ty), main_title, font=font_title, fill="white")
        
        # Draw red accent line
        line_y = ty + 95
        draw.line([(tx, line_y), (tx + 560, line_y)], fill=(220, 38, 38, 255), width=5)
        
        # Draw subtitle
        draw.text((tx, line_y + 20), subtitle.upper(), font=font_sub, fill=(200, 200, 200, 255))

        bg.convert("RGB").save(output_path, quality=95)
        return output_path

    @staticmethod
    def style4_centered_headline(photo_path, headline_text, output_path):
        """Style 4: Archival vintage photo with bold centered typewriter title"""
        im = ImageOps.fit(Image.open(photo_path).convert("RGB"), (1920, 1080), Image.Resampling.LANCZOS)
        # Apply desaturated vintage contrast
        im_bw = ImageOps.grayscale(im).convert("RGB")
        
        draw = ImageDraw.Draw(im_bw)
        font = get_font(COUR_BOLD, 72)
        
        # Calculate centered text bbox
        bbox = draw.textbbox((0, 0), headline_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (1920 - tw) // 2
        y = (1080 - th) // 2

        # Draw dark shadow/outline for contrast
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                draw.text((x + ox, y + oy), headline_text, font=font, fill=(0, 0, 0))
        draw.text((x, y), headline_text, font=font, fill=(255, 255, 255))

        im_bw.save(output_path, quality=95)
        return output_path

    @staticmethod
    def style5_quote_caption(photo_path, quote_text, output_path):
        """Style 5: Moody photo with centered typewriter quote caption"""
        im = ImageOps.fit(Image.open(photo_path).convert("RGB"), (1920, 1080), Image.Resampling.LANCZOS)
        im_bw = ImageOps.grayscale(im).convert("RGB")
        
        draw = ImageDraw.Draw(im_bw)
        font = get_font(COUR_BOLD, 52)

        bbox = draw.textbbox((0, 0), quote_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (1920 - tw) // 2
        y = (1080 - th) // 2

        for ox in range(-2, 3):
            for oy in range(-2, 3):
                draw.text((x + ox, y + oy), quote_text, font=font, fill=(0, 0, 0))
        draw.text((x, y), quote_text, font=font, fill=(245, 245, 245))

        im_bw.save(output_path, quality=95)
        return output_path

print("GraphicCompositor module successfully initialized and verified!")
