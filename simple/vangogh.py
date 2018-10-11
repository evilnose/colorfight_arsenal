import cf_client

if __name__ == '__main__':
    g = cf_client.Game()

    if g.join('Van Gogh'):
        w = g.width
        h = g.height
        indices = draw(w, h)
        for x, y in indices:
           c = g.get_cell(x, y)
