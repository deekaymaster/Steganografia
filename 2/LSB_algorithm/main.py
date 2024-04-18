from PIL import Image

class Steganography:
    @staticmethod
    def create_color_matrix(container_path, output_matrix_r_path, output_matrix_g_path, output_matrix_b_path):
        container = Image.open(container_path)

        # Tworzymy trzy obrazy o takich samych wymiarach jak obraz wejściowy
        container_r = Image.new("1", container.size) # Głębia bitowa 1 oznacza, że każdy piksel w tym obrazie może przyjmować tylko dwie możliwe wartości: 0 (czarny) lub 255 (biały)
        container_g = Image.new("1", container.size)
        container_b = Image.new("1", container.size)

        for y in range(container.height):
            for x in range(container.width):
                pixel = container.getpixel((x, y))  # Pobieramy piksel na pozycji x, y

                # Pobieramy wartości składowych R, G, B
                r, g, b = pixel

                # Sprawdzamy najmłodszy bit składowej R, G, B
                r_bit = r & 1  # Najmłodszy bit składowej R
                g_bit = g & 1  # Najmłodszy bit składowej G
                b_bit = b & 1  # Najmłodszy bit składowej B

                # Zapisujemy piksel jako czarny (0) lub biały (1) w zależności od wartości najmłodszego bitu
                container_r.putpixel((x, y),
                                     255 if r_bit else 0)  # Biały (255) jeśli bit R jest ustawiony, czarny (0) w przeciwnym przypadku
                container_g.putpixel((x, y),
                                     255 if g_bit else 0)  # Biały (255) jeśli bit G jest ustawiony, czarny (0) w przeciwnym przypadku
                container_b.putpixel((x, y),
                                     255 if b_bit else 0)  # Biały (255) jeśli bit B jest ustawiony, czarny (0) w przeciwnym przypadku

        # Zapisujemy trzy osobne obrazy dla każdej składowej koloru
        container_r.save(output_matrix_r_path)
        container_g.save(output_matrix_g_path)
        container_b.save(output_matrix_b_path)

    @staticmethod
    def embed_lsb(container_path, message, output_path):
        container = Image.open(container_path)

        # Konwertuję wiadomość na postać binarną.
        binary_message = ''.join(format(ord(char), '08b') for char in message)
        binary_message += '1111111111111110'  # Dodaję marker końca komunikatu.

        message_length = len(binary_message)
        if message_length > container.width * container.height * 3:
            raise ValueError("Wiadomość jest zbyt długa, aby schować ją w wybranym kontenerze")

        index = 0  # Indeks służy do przemieszczania się po kolejnych bitach wiadomości.
        for y in range(container.height):
            for x in range(container.width):
                if index < len(binary_message):
                    pixel = list(container.getpixel((x, y)))  # Pobieram piksel na pozycji x, y.
                    for i in range(3):  # Dla każdej składowej koloru (RGB).
                        if index < len(binary_message):
                            # Zeruję najmniej znaczący bit za pomocą operacji logicznego AND z maską 0b11111110, a następnie ustawiam bit wiadomości.
                            pixel[i] = pixel[i] & 0b11111110 | int(binary_message[index], 2)
                            index += 1
                    # Zapisuję zmodyfikowany piksel do obrazu.
                    container.putpixel((x, y), tuple(pixel))
                else:
                    container.save(output_path)
                    return

    @staticmethod
    def embed_msb(container_path, message, output_path):
        container = Image.open(container_path)

        # Konwertuję wiadomość na postać binarną.
        binary_message = ''.join(format(ord(char), '08b') for char in message)
        binary_message += '1111111111111110'  # Dodaję marker końca komunikatu.

        message_length = len(binary_message)
        if message_length > container.width * container.height * 3:
            raise ValueError("Wiadomość jest zbyt długa, aby schować ją w wybranym kontenerze")

        index = 0
        for y in range(container.height):
            for x in range(container.width):
                if index < len(binary_message):
                    pixel = list(container.getpixel((x, y)))
                    for i in range(3):  # Dla każdej składowej koloru (RGB).
                        if index < len(binary_message):
                            # Zeruję najbardziej znaczący bit, a następnie ustawiam bit wiadomości.
                            pixel[i] = pixel[i] & 0b01111111 | int(binary_message[index], 2) << 7  # << 7 przesuwa wartość o 7 pozycji bitowych w lewo.
                            index += 1
                    container.putpixel((x, y), tuple(pixel))
                else:
                    container.save(output_path)
                    return

    @staticmethod
    def extract_lsb(container_path):
        container = Image.open(container_path)
        binary_message = ''
        for y in range(container.height):
            for x in range(container.width):
                pixel = container.getpixel((x, y))
                for color in pixel:
                    binary_message += bin(color)[-1]  # Pobieram ostatni bit każdej składowej koloru i dodaje do wiadomości.
        end_marker_index = binary_message.find('1111111111111110')
        if end_marker_index != -1:
            binary_message = binary_message[:end_marker_index]
            message = ''
            for i in range(0, len(binary_message), 8):  # Dzielę ciąg znaków na 8-bitowe fragmenty.
                message += chr(int(binary_message[i:i + 8], 2))  # Zamieniam każdy 8-bitowy fragment na znak ASCII i dodaję do zmiennej wiadomości.
            return message
        else:
            raise ValueError("Nie znaleziono markera końca wiadomości")

    @staticmethod
    def extract_msb(container_path):
        container = Image.open(container_path)
        binary_message = ''
        for y in range(container.height):
            for x in range(container.width):
                pixel = container.getpixel((x, y))
                for color in pixel:
                    binary_message += bin(color & 0b10000000)[2]  # Pobieram najbardziej znaczący bit każdej składowej koloru.
        end_marker_index = binary_message.find('1111111111111110')
        if end_marker_index != -1:
            binary_message = binary_message[:end_marker_index]
            message = ''
            for i in range(0, len(binary_message), 8):  # Dzielę ciąg znaków na 8-bitowe fragmenty.
                message += chr(int(binary_message[i:i + 8], 2))  # Zamieniam każdy 8-bitowy fragment na znak ASCII i dodaję do zmiennej wiadomości.
            return message
        else:
            raise ValueError("Nie znaleziono markera końca wiadomości")


# Osadzam komunikat w obrazie BMP algorytmem LSB (najmniej znaczący bit)
container_path = 'sample.bmp'
first_message = "Kogut Dawid Piotr"
second_message = "Platforma stosujaca steganografie do ukrywania tekstow w obrazach, niezaleznie od formatu pliku (BMP, PNG, JPG), zapewnia wysoki poziom bezpieczenstwa danych. Mechanizmy steganograficzne sa skuteczne w ukrywaniu informacji, co utrudnia dostep osobom nieuprawnionym, az do momentu wykrycia metody stosowanej przez platforme. Wizualne efekty ukrywania tekstu w obrazkach sa tak subtelne, ze ludzkie oko nie jest w stanie wykryc roznic na pierwszy rzut oka. Nawet przy uzyciu roznych formatow plikow (BMP, PNG, JPG), efekt ukrywania jest niezauwazalny dla przecietnego uzytkownika. Istotne jest, ze proces ukrywania tekstu w obrazach nie wplywa negatywnie na jakosc obrazow. Nawet przy szczegolowych analizach, dopiero roznice w obrazie Malewicza mogly byc zauwazone tylko przy uzyciu przyblizenia i to na obszarach o jednolitych kolorach, co swiadczy o wysokiej jakosci steganografii stosowanej przez platforme. Metody odzyskiwania danych z zakodowanych tekstow w obrazach dzialaja bez zarzutow. Proces odkodowywania ukrytych informacji jest sprawny i nie wymaga specjalistycznych narzedzi czy zaawansowanej wiedzy. Problemem platformy jest to, ze kazdy obraz po zakodowaniu w nim tekstu jest generowany w formacie PNG niezaleznie od formatu zrodlowego. Uwazam, ze ten problem moze miec wplyw na ocene dzialania platformy dla roznych formatow plikow graficznych."
output_first_lsb_path = 'output_first_lsb.bmp'
output_second_lsb_path = 'output_second_lsb.bmp'
Steganography.embed_lsb(container_path, first_message, output_first_lsb_path)
Steganography.embed_lsb(container_path, second_message, output_second_lsb_path)

# Wydobywam komunikat z osadzonego obrazu BMP algorytmem LSB
extracted_first_message_lsb = Steganography.extract_lsb(output_first_lsb_path)
extracted_second_message_lsb = Steganography.extract_lsb(output_second_lsb_path)

print("Pierwsza wiadomość odczytana z kontenera, w którym zakodowano ją algorytmem LSB:", extracted_first_message_lsb)
print("Druga wiadomość odczytana z kontenera, w którym zakodowano ją algorytmem LSB:", extracted_second_message_lsb)

# Osadzam komunikat w obrazie BMP algorytmem MSB (najbardziej znaczący bit)
output_first_msb_path = 'output_first_msb.bmp'
output_second_msb_path = 'output_second_msb.bmp'
Steganography.embed_msb(container_path, first_message, output_first_msb_path)
Steganography.embed_msb(container_path, second_message, output_second_msb_path)

# Wydobywam komunikat z osadzonego obrazu BMP algorytmem MSB
extracted_first_message_msb = Steganography.extract_msb(output_first_msb_path)
extracted_second_message_msb = Steganography.extract_msb(output_second_msb_path)

print("Pierwsza wiadomość odczytana z kontenera, w którym zakodowano ją algorytmem MSB:", extracted_first_message_msb)
print("Druga wiadomość odczytana z kontenera, w którym zakodowano ją algorytmem MSB:", extracted_second_message_msb)

# Tworze 3 macierze kolorów dla: R,G,B
Steganography.create_color_matrix(container_path, "matrix_r.bmp", "matrix_g.bmp", "matrix_b.bmp")