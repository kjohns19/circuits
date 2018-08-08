import cairo


def draw_text(cr, text, position, bold=False):
    weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
    cr.set_source_rgb(0, 0, 0)
    cr.select_font_face(
        'FreeSans',
        cairo.FONT_SLANT_NORMAL,
        weight)
    cr.set_font_size(12)

    x, y, w, h, dx, dy = cr.text_extents(text)

    cr.move_to(*(position - (w/2, -h/2)))
    cr.show_text(text)
