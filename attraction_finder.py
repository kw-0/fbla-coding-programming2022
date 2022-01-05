import pygame
from pathlib import Path

pygame.init()
clock = pygame.time.Clock()
fps = 60
main_bg = (60, 80, 177)
red = (219, 41, 41)
light_red = (237, 100, 100)
black = (19, 19, 19)
grey = (200, 200, 200)

def button(window, text, button_color, rollover_change_color, location, width=225, height=200, text_location=None, font="Montserrat", text_color=black, text_size=45):
    # window is the window it opens, must be a  pygame.display.set_mode(size) window
    mouse_pos = pygame.mouse.get_pos()
    x, y = location

    global rectangle
    rectangle = pygame.Rect(x, y, width, height)

    font = pygame.font.SysFont(font, text_size)
    text = [font.render(text, True, text_color) for text in text.split()] 

    if (location[0] < mouse_pos[0] < location[0] + width and location[1] < mouse_pos[1] < location[1] + height):
        pygame.draw.rect(window, rollover_change_color, rectangle, border_radius=20)
    else:
        pygame.draw.rect(window, button_color, rectangle, border_radius=20)

    if text_location:
        for i, word in enumerate(text):
            window.blit(word, (text_location[0], (text_location[1] + i * 40)))
    else:
        if len(text) == 1:
            window.blit(text[0], text[0].get_rect(center=((x + ((width / 2)), (y + (height / 2))))))
        elif len(text) == 2:
            for i, word in enumerate(text):
                window.blit(word, word.get_rect(center=((x + ((width / 2)), ((y + i * 40) + (height / 2)) - 15))))
        else:
            for i, word in enumerate(text):
                window.blit(word, word.get_rect(center=((x + ((width / 2)), ((y + i * 40) + (height / 2)) - 45))))

# instead of building a diffrent function for each window, i just plug-and-play with different attraction types
def attraction_type(type, screen, screen_width, screen_height, run_type, bg_color, attractions_list, search_type=None, search_attribute=None):
    run_main = False
    run_search = False

    init_attractions = True
    while run_type:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            screen.fill(bg_color)
            if event.type == pygame.QUIT:
                pygame.quit()

            title = pygame.font.SysFont("Montserrat", 150).render(type, True, black)

            if search_type is not None and search_attribute is not None:
                search_type_list = ["info", "type", 0, "city", "age_range", "rating", "size"]

                search_type_idx = search_type_list.index(search_type.lower())
                searched_attractions_list = []
                for attraction in attractions_list:
                    if attraction.info_list[search_type_idx].lower() == search_attribute.lower():
                        searched_attractions_list.append(attraction)
                attractions_list = searched_attractions_list.copy()

            # shows the attractions at their starting locations, then if down or up is hit it moves them and stops showing the original
            if init_attractions == True:
                screen.blit(title, title.get_rect(center=(screen_height / 2, (screen_width / 2)-350)))
                
                for i, attraction in enumerate(attractions_list):
                    attraction.show(first_position=(53, 200), attraction_num=i, scroll_count=0)

                    if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                        print(f"clicked: {attraction.name}")
                        attraction.on_click()

                # checks if the user scrolls the screen, if they do then add one to scroll count in that directtion
                if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    init_attractions = False
                    scroll_count = -1
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    init_attractions = False
                    scroll_count = 1
            else:
                for i, attraction in enumerate(attractions_list):
                    attraction.show(first_position=(53, 200), attraction_num=i, scroll_count=scroll_count)

                    if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                        print(f"clicked: {attraction.name}")
                        attraction.on_click()

                    if scroll_count < 0:
                        scroll_count = -1
                    
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN :
                        scroll_count -= 1
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                        scroll_count += 1
                screen.blit(title, title.get_rect(center=(screen_height / 2, (screen_width / 2)-(350+scroll_count*9))))

                # need both of these because the gloabl rectangle gets redefined each time
                if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                    print(f"clicked: {attraction.name}")
                    attraction.on_click()

            if search_type is None and search_attribute is None:
                button(screen, "Search", (255, 166, 83), (255, 211, 89), (1225, 35), width=150, height=50)
                if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                    run_type = False
                    run_search = True

            button(screen, "Back", (255, 166, 83), (255, 211, 89), (50, 35), width=100, height=50)
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                run_type = False
                run_main = True

            pygame.display.update()
            clock.tick(fps)
    return run_main, run_search

# remember it needs 5+ search criterion on the attraction type pages
class attraction:
    def __init__(self, name, window, info_list, color=red, rollover_color=light_red, size=(50, 200)):
        # should draw the rectangle with info about the attracion with just the attraction info input
        self.name = name
        self.window = window
        self.info_list = info_list 
        """
        the info list will be structured like the atttractions txt file:
            [info, type, 2 pics filepath, address, age_range, popularity/rating, size]
        """
        self.color = color
        self.rollover_color = rollover_color  # make function to go from color to rollover color, but not in button code b/c we want to be able to make it smthg different in the button code
        
        self.size = size

    def show(self, first_position, attraction_num, scroll_count):
        mouse_pos = pygame.mouse.get_pos()
        vert_position_offset = 10
        hori_position_offset = 35

        # calculates position of the attraction based on size, row, scroll, and number of attractions
        scroll_amt = -5*scroll_count
        if attraction_num % 4 == 0: # checks if the attraction should go on the next row and puts it there if so
            row_num = attraction_num/4
            summed_row_sizes = row_num*self.size[1]
            summed_row_offsets = row_num*vert_position_offset
  
            self.position = (first_position[0],  first_position[1]+(summed_row_offsets+summed_row_sizes+scroll_amt))
            
        else:
            row_num = int(attraction_num/4)  # by turning it into an int it cuts off any ending digits
            summed_row_sizes = row_num*self.size[1]
            summed_row_offsets = row_num*vert_position_offset

            # keeps the user from scrolling too low on the screen   
            if attraction_num>4:  attractions_in_row = attraction_num%4
            else:                 attractions_in_row = attraction_num

            summed_attraction_sizes = attractions_in_row*self.size[0]
            summed_attraction_hori_offsets = attractions_in_row*hori_position_offset

            self.position = (first_position[0]+summed_attraction_sizes+summed_attraction_hori_offsets,first_position[1]+(summed_row_offsets+summed_row_sizes+scroll_amt))

        # draws the rectangle (w/ rollover color)
        global rectangle # enables .on_click
        rectangle = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
        if (self.position[0] < mouse_pos[0] < self.position[0] + self.size[0] and self.position[1] < mouse_pos[1] < self.position[1] + self.size[1]):
            pygame.draw.rect(self.window, self.rollover_color, rectangle, border_radius=20)
        else:
            pygame.draw.rect(self.window, self.color, rectangle, border_radius=20)
        
        # types the title with a line break at 2 words because it is a bigger font
        title_font = pygame.font.SysFont("Montserrat", 40)
        title = self.name.split()
        for i in range(len(title)):
            if not((i*2)+2 > len(title)):
                basic_info = title_font.render(" ".join(title[(i*2):(i*2)+2]), True, black)
                self.window.blit(basic_info, basic_info.get_rect(center=((self.position[0] + ((self.size[0] / 2)), (self.position[1] + (self.size[1] / 2))-250+(i*23)))))
            else:
                basic_info = title_font.render(" ".join(title[(i*2):]), True, black)
                self.window.blit(basic_info, basic_info.get_rect(center=((self.position[0] + ((self.size[0] / 2)), (self.position[1] + (self.size[1] / 2))-250+(i*23)))))

        # types ONE sentence of the info
        # puts the first sentence into a list with 5 words per space in list
        info_font = pygame.font.SysFont("Montserrat",  25)
        raw_info_text = self.info_list[0]
        info_sentence = raw_info_text.split(".")[0].split()
        for i in range(len(info_sentence)):
            if not((i*5)+5 > len(info_sentence)):
                basic_info = info_font.render(" ".join(info_sentence[(i*5):(i*5)+5]), True, black)
                self.window.blit(basic_info, basic_info.get_rect(center=((self.position[0] + (self.size[0] / 2), (self.position[1] + (self.size[1] / 2))-190+(i*15)))))
            else:
                basic_info = info_font.render(" ".join(info_sentence[(i*5):]), True, black)
                self.window.blit(basic_info, basic_info.get_rect(center=((self.position[0] + (self.size[0] / 2), (self.position[1] + (self.size[1] / 2))-190+(i*15)))))
        
        # shows the type on the widget
        attraction_type = self.info_list[1]
        attraction_type_font = pygame.font.SysFont("Montserrat",  20)

        attraction_type = attraction_type_font.render(f"Type: {attraction_type}", True, black)
        self.window.blit(attraction_type, attraction_type.get_rect(center=((self.position[0] + (self.size[0] / 2), (self.position[1] + (self.size[1] / 2))+60))))

        # loads the first photo (small, scaled (aspect ratio maintained) version)
        image_path = Path(self.info_list[2].split()[0])
        image = pygame.image.load(image_path)

        img_offset = 20
        aspect_ratio = image.get_height()/image.get_width() # this calculates what scale factor is needed to have exactly the offset distance at both sides of the image
        width = self.size[0] - 2*img_offset
        height = round(aspect_ratio * width)
        image = pygame.transform.scale(image, (width, height))

        self.window.blit(image, (self.position[0]+img_offset, self.position[1]+130))

        # types the address on the widget
        info_font = pygame.font.SysFont("Montserrat",  20)

        address = self.info_list[3]
        address = info_font.render(f"Address: {address}", True, black)
        self.window.blit(address, address.get_rect(center=((self.position[0] + (self.size[0] / 2), (self.position[1] + (self.size[1] / 2))+100))))

        # types the age range on the widget
        # should say Age Range: All, Adult, Children, Teen, etc.
        age_range = self.info_list[4]
        age_range = info_font.render(f"Age Range: {age_range}", True, black)
        self.window.blit(age_range, age_range.get_rect(center=((self.position[0] + (self.size[0] / 2), (self.position[1] + (self.size[1] / 2))+140))))

        # types the average rating  of that attraction
        # if should say Rating: <rating here>
        rating = self.info_list[5]
        rating = info_font.render(f"Rating: {rating}", True, black)
        self.window.blit(rating, rating.get_rect(center=((self.position[0] + (self.size[0] / 2), (self.position[1] + (self.size[1] / 2))+180))))

        # types the size of the attraction
        size = self.info_list[6]
        size = info_font.render(f"Size: {size}", True, black)
        self.window.blit(size, size.get_rect(center=((self.position[0] + (self.size[0] / 2), (self.position[1] + (self.size[1] / 2))+220))))

    def on_click(self):
        # should open the attraction page when clicked, the page should have:
        # a back button
        # info about it
        # a like button to keep track of things the signed in user liked and disliked for reccomendations
        # reccomendations should have a randomization value (use some greek letter for it maybe epsilon) where it will randomly show some random attractions outside of just things you liked
        show_info = True
        while show_info:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                # background
                bg_x, bg_y, bg_width, bg_height = 20, 20, 1400, 860
                rectangle = pygame.Rect(bg_x, bg_y, bg_width, bg_height)
                pygame.draw.rect(self.window, light_red, rectangle, border_radius=30)

                # title
                title = pygame.font.SysFont("Montserrat", 100)
                title = title.render(self.name, True, black)
                screen.blit(title, title.get_rect(center=(screen_height / 2, (screen_width / 2)-350)))

                # information text
                info_font = pygame.font.SysFont("Montserrat",  28)
                raw_info_text = self.info_list[0]
                info_sentence = raw_info_text.split()

                info_x, info_y, info_width, info_height = 60, 200, 450, 600

                info_rectangle = pygame.Rect(info_x, info_y, info_width, info_height)
                pygame.draw.rect(self.window, grey, info_rectangle, border_radius=20)

                for i in range(len(info_sentence)):
                    if not((i*5)+5 > len(info_sentence)):
                        basic_info = info_font.render(" ".join(info_sentence[(i*5):(i*5)+5]), True, black) # seven here instead of 5 b/c this is for the 
                        self.window.blit(basic_info, basic_info.get_rect(center=((info_x + ((info_width / 2)), (info_y + (info_height / 2) - 270 + (i*20))))))
                    else:
                        basic_info = info_font.render(" ".join(info_sentence[(i*5):]), True, black)
                        self.window.blit(basic_info, basic_info.get_rect(center=((info_x + ((info_width / 2)), (info_y + (info_height / 2) - 270 + (i*20))))))

                # shows image 2 but bigger
                image_paths = self.info_list[2].split()

                # widths = []
                for i, image_path in enumerate(image_paths):

                    image = pygame.image.load(Path(image_path))

                    img_offset = 30

                    aspect_ratio = image.get_height()/image.get_width()
                    width = 400
                    # widths.append(width)
                    img_height = round(aspect_ratio * width) # this calculates what scale factor is needed to have exactly the offset distance at both sides of the image
                    image = pygame.transform.scale(image, (width,img_height))

                    img_y = info_y-30

                    if i==0:
                        self.window.blit(image, ((info_x + info_width + img_offset)+i*20, img_y))
                    else:
                        self.window.blit(image, ((info_x + info_width + img_offset)+width+i*20, img_y))

                # information text
                # info_font = pygame.font.SysFont("Montserrat",  25)
                # raw_info_text = self.info_list[0]
                # info_sentence = raw_info_text.split()

                # extra_info
                extra_info_font = pygame.font.SysFont("Montserrat",  50)

                extra_info_x = (info_x + info_width + img_offset)
                extra_info_y = (img_y+img_height+60)
                extra_info_width = 830
                extra_info_height = info_height-info_y-60

                extra_info_rectangle = pygame.Rect(extra_info_x, extra_info_y, extra_info_width, extra_info_height)
                pygame.draw.rect(self.window, grey, extra_info_rectangle, border_radius=20)

                # types the type on the screen
                attraction_type = self.info_list[1]
                attraction_type = extra_info_font.render(f"Type: {attraction_type}", True, black)
                self.window.blit(attraction_type, attraction_type.get_rect(center=((extra_info_x + (extra_info_width / 2), (extra_info_y + (extra_info_height / 2))-120))))

                # types the address on the extra info screen
                address = self.info_list[3]
                address = extra_info_font.render(f"Address: {address}", True, black)
                self.window.blit(address, address.get_rect(center=((extra_info_x + (extra_info_width / 2), (extra_info_y + (extra_info_height / 2))-60))))

                # types the age range on the widget
                # should say Age Range: All, Adult, Children, Teen, etc.
                age_range = self.info_list[4]
                age_range = extra_info_font.render(f"Age Range: {age_range}", True, black)
                self.window.blit(age_range, age_range.get_rect(center=((extra_info_x + (extra_info_width / 2), (extra_info_y + (extra_info_height / 2))))))

                # types the average rating  of that attraction
                # if should say Rating: <rating here>
                rating = self.info_list[5]
                rating = extra_info_font.render(f"Rating: {rating}", True, black)
                self.window.blit(rating, rating.get_rect(center=((extra_info_x + (extra_info_width / 2), (extra_info_y + (extra_info_height / 2))+60))))

                # types the size of the attraction
                size = self.info_list[6]
                size = extra_info_font.render(f"Size: {size}", True, black)
                self.window.blit(size, size.get_rect(center=((extra_info_x + (extra_info_width / 2), (extra_info_y + (extra_info_height / 2))+120))))

                button(screen, "Back", (255, 166, 83), (255, 211, 89), (55, 40), width=100, height=50)
                if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                    show_info = False

                pygame.display.update()
                clock.tick(fps)

def search_screen(category, search_type, attractions_list, *search_items):
        purple = (162, 36, 173)
        light_purple = (171, 0, 255)
        button_origin = (0, 0)
        button_spacing = 0
        # 4 search iteams
        # search type will be either "type", "city", "size", and "age_range"
        search_screen = True
        while search_screen:
            type_to_search = None
            mouse_pos = pygame.mouse.get_pos()
            screen.fill(main_bg)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                title = pygame.font.SysFont("Montserrat", 125).render("Select a Category!", True, black)
                screen.blit(title, title.get_rect(center=(screen_height / 2, (screen_width / 2) - 350)))

        
                button_origin = (350, 350)
                button_spacing = 53

                for i in range(len(search_items)):
                    button(screen, search_items[i], purple, light_purple, (button_origin[0] + (i * 225) + (i*button_spacing), 350))
                    if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                        type_to_search = search_items[i]
                        search_screen = False


                button(screen, "Back", red, light_red, (55, 40), width=100, height=50)
                if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                    search_screen = False
                
                pygame.display.update()
                clock.tick(fps)
        return type_to_search


screen = pygame.display.set_mode((1440, 900))
screen_height, screen_width = screen.get_size()

pygame.display.set_caption("Florida Attractions")

run_main = True
run_search = False
run_museums, run_restaurants, run_amusement, run_parks, run_music =  False, False, False, False, False


while True:
    while run_main:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            screen.fill(main_bg)
            if event.type == pygame.QUIT:
                pygame.quit()


            title = pygame.font.SysFont("Montserrat", 160).render("Attractions in Florida!", True, black)
            screen.blit(title, title.get_rect(center=(screen_height / 2, (screen_width / 2) - 300)))
            bottom_title = pygame.font.SysFont("Montserrat", 160).render("Click One to Begin", True, black)
            screen.blit(bottom_title, bottom_title.get_rect(center=(screen_height / 2, (screen_width / 2) + 300)))

            button_origin = (53, 330)
            button_spacing = 53
            
            
            button(screen, "Museums", red, light_red, button_origin)
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                run_museums = True

                with open("attractions.txt", "r") as attractions:
                    attractions = attractions.readlines()
                    begin_idx = attractions.index("museums\n")
                    end_idx = attractions.index("restaurants\n")
                    attractions = [word.replace("\n", "") for word in attractions[begin_idx+1:end_idx]]

                attractions_list =[]
                for i in range(round(len(attractions)/8)):
                    info = attractions[(i*8):(i*8)+8]
                    attr = attraction(info[0], window=screen, info_list=info[1:8], size=(300, 550))
                    attractions_list.append(attr)
                
                run_main, run_search = attraction_type("Museums", screen, screen_width, screen_height, run_museums, main_bg, attractions_list)
                category = "Museums"

            button(screen, "Restaurants", red, light_red, (button_origin[0] + 225 + button_spacing, button_origin[1]))
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                
                run_restaurants = True

                with open("attractions.txt", "r") as attractions:
                    attractions = attractions.readlines()
                    begin_idx = attractions.index("restaurants\n")
                    end_idx = attractions.index("amusement\n")
                    attractions = [word.replace("\n", "") for word in attractions[begin_idx+1:end_idx]]

                attractions_list =[]
                for i in range(round(len(attractions)/8)):
                    info = attractions[(i*8):(i*8)+8]
                    attr = attraction(info[0], window=screen, info_list=info[1:8], size=(300, 550))
                    attractions_list.append(attr)
                
                run_main, run_search = attraction_type("Restaurants", screen, screen_width, screen_height, run_restaurants, main_bg, attractions_list)
                category = "Restaurants"

            button(screen, "Amusement Parks", red, light_red, (button_origin[0] + (2 * 225) + (2 * button_spacing), button_origin[1]))
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                run_amusement = True

                with open("attractions.txt", "r") as attractions:
                    attractions = attractions.readlines()
                    begin_idx = attractions.index("amusement\n")
                    end_idx = attractions.index("parks\n")
                    attractions = [word.replace("\n", "") for word in attractions[begin_idx+1:end_idx]]

                attractions_list =[]
                for i in range(round(len(attractions)/8)):
                    info = attractions[(i*8):(i*8)+8]
                    attr = attraction(info[0], window=screen, info_list=info[1:8], size=(300, 550))
                    attractions_list.append(attr)
                
                run_main, run_search = attraction_type("Amusement Parks", screen, screen_width, screen_height, run_amusement, main_bg, attractions_list)
                category = "Amusement"


            button(screen,"Parks and Recreation",red, light_red, (button_origin[0] +(3 * 225) + (3 * button_spacing), button_origin[1])) 
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                run_parks = True

                with open("attractions.txt", "r") as attractions:
                    attractions = attractions.readlines()
                    begin_idx = attractions.index("parks\n")
                    end_idx = attractions.index("music\n")
                    attractions = [word.replace("\n", "") for word in attractions[begin_idx+1:end_idx]]

                attractions_list =[]
                for i in range(round(len(attractions)/8)):
                    info = attractions[(i*8):(i*8)+8]
                    attr = attraction(info[0], window=screen, info_list=info[1:8], size=(300, 550))
                    attractions_list.append(attr)
                
                run_main, run_search = attraction_type("Parks and Recreation", screen, screen_width, screen_height, run_parks, main_bg, attractions_list)
                category = "Parks"

            button(screen, "Music and Arts", red, light_red, (button_origin[0] + (4 * 225) + (4 * button_spacing), button_origin[1]))
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                run_music = True

                with open("attractions.txt", "r") as attractions:
                    attractions = attractions.readlines()
                    begin_idx = attractions.index("music\n")
                    end_idx = attractions.index("END\n")
                    attractions = [word.replace("\n", "") for word in attractions[begin_idx+1:end_idx]]

                attractions_list =[]
                for i in range(round(len(attractions)/8)):
                    info = attractions[(i*8):(i*8)+8]
                    attr = attraction(info[0], window=screen, info_list=info[1:8], size=(300, 550))
                    attractions_list.append(attr)
                
                run_main, run_search = attraction_type("Music and Arts", screen, screen_width, screen_height, run_music, main_bg, attractions_list)
                category = "Music"

            pygame.display.update()
            clock.tick(fps)

    while run_search:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            screen.fill(main_bg)
            if event.type == pygame.QUIT:
                pygame.quit()

            title = pygame.font.SysFont("Montserrat", 150).render("Search by:", True, black)
            screen.blit(title, title.get_rect(center=(screen_height / 2, (screen_width / 2) - 350)))
            button_origin = (210, 350)
            button_spacing = 53
    
            button(screen, "Type", red, light_red, button_origin)
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos): 
                if category == "Museums":
                    search_attribute = search_screen(category, "Type", attractions_list, "Science", "Memorial", "History")
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_museums, main_bg, attractions_list, search_type="type", search_attribute=search_attribute)
                elif category == "Restaurants":
                    search_attribute = search_screen(category, "Type", attractions_list, "Steak", "Indian", "General")
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_restaurants, main_bg, attractions_list, search_type="type", search_attribute=search_attribute)
                elif category == "Amusement":
                    search_attribute = search_screen(category, "Type", attractions_list, "Themed", "Rides and Rollercoasters", "Other")
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_amusement, main_bg, attractions_list, search_type="type", search_attribute=search_attribute)
                elif category == "Parks":
                    search_attribute = search_screen(category, "Type", attractions_list, "Parks", "Zoos/Aquariums", "Recreation")
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_parks, main_bg, attractions_list, search_type="type", search_attribute=search_attribute)
                elif category == "Music":
                    search_attribute = search_screen(category, "Type", attractions_list, "Live Music", "Art Museum", "Art Gallery")
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_music, main_bg, attractions_list, search_type="type", search_attribute=search_attribute)

                run_main = True
                run_search = False
                

            button(screen, "City", red, light_red, (button_origin[0] + 225 + button_spacing, 350))
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                search_attribute = search_screen(category, "City", attractions_list, "Orlando", "Tampa", "Sarasota")
                if category == "Museums":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_museums, main_bg, attractions_list, search_type="city", search_attribute=search_attribute)
                elif category == "Restaurants":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_restaurants, main_bg, attractions_list, search_type="city", search_attribute=search_attribute)
                elif category == "Amusement":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_amusement, main_bg, attractions_list, search_type="city", search_attribute=search_attribute)
                elif category == "Parks":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_parks, main_bg, attractions_list, search_type="city", search_attribute=search_attribute)
                elif category == "Music":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_music, main_bg, attractions_list, search_type="city", search_attribute=search_attribute)

                run_main = True
                run_search = False

            button(screen, "Age Range", red, light_red, (button_origin[0] + (2 * 225) + (2 * button_spacing), 350) )
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                search_attribute = search_screen(category, "Age Range", attractions_list, "Children", "Teens and Adults", "Everyone")
                if category == "Museums":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_museums, main_bg, attractions_list, search_type="age_range", search_attribute=search_attribute)
                elif category == "Restaurants":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_restaurants, main_bg, attractions_list, search_type="age_range", search_attribute=search_attribute)
                elif category == "Amusement":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_amusement, main_bg, attractions_list, search_type="age_range", search_attribute=search_attribute)
                elif category == "Parks":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_parks, main_bg, attractions_list, search_type="age_range", search_attribute=search_attribute)
                elif category == "Music":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_music, main_bg, attractions_list, search_type="age_range", search_attribute=search_attribute)

                run_main = True
                run_search = False

            button(screen, "Size", red, light_red, (button_origin[0] + (3 * 225) + (3 * button_spacing), 350))
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                search_attribute = search_screen(category, "Size", attractions_list, "Small", "Medium", "Large")
                if category == "Museums":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_museums, main_bg, attractions_list, search_type="size", search_attribute=search_attribute)
                elif category == "Restaurants":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_restaurants, main_bg, attractions_list, search_type="size", search_attribute=search_attribute)
                elif category == "Amusement":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_amusement, main_bg, attractions_list, search_type="size", search_attribute=search_attribute)
                elif category == "Parks":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_parks, main_bg, attractions_list, search_type="size", search_attribute=search_attribute)
                elif category == "Music":
                    run_main, run_search = attraction_type(category, screen, screen_width, screen_height, run_music, main_bg, attractions_list, search_type="size", search_attribute=search_attribute)

                run_main = True
                run_search = False

            button(screen, "Back", red, light_red, (50, 35), width=100, height=50)
            if event.type == pygame.MOUSEBUTTONDOWN and rectangle.collidepoint(mouse_pos):
                run_search = False
                run_main = True

            pygame.display.update()
            clock.tick(fps)