def diagonal(matrixLength):
    matrixLength -= 1
    coords = []
    coordsB = []
    for i in range(matrixLength):
        if i % 2 == 0:
            x = i
            y = 0
            while y <= i:
                coord = (x, y)
                coords.append(coord)
                y += 1
                x -= 1

        elif i % 2 == 1:
            x = 0
            y = i
            while x <= i:
                coord = (x, y)
                coords.append(coord)
                x += 1
                y -= 1
    for i in range(matrixLength, -1, -1):
        if i % 2 == 1:
            x = i
            y = matrixLength
            while y >= i:
                coord = (x, y)
                coordsB.insert(0, coord)
                y -= 1
                x += 1

        elif i % 2 == 0:
            x = matrixLength
            y = i
            while x >= i:
                coord = (x, y)
                coordsB.insert(0, coord)
                x -= 1
                y += 1
    coords += coordsB
    return coords


# Takes square matrices and returns coordinates for LED's
# e.g. 8x8 LED matrix, matrixLength = 8
def straight(matrixLength):
    coords = []
    for i in range(matrixLength):
        x = 0
        y = i
        while x < matrixLength:
            coord = (x, y)
            coords.append(coord)
            x += 1
    return coords
