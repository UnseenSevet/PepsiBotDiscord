from PIL import Image, ImageDraw, ImagePath, ImageOps
import math
import re
import colorsys
import os



def bsona(namex):
    #list of states in population order
    states = ["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI", "NJ", "VA", "WA", "AZ", "TN", "MA", "IN", "MO", "MD", "WI", "CO", "MN", "SC", "AL", "LA", "KY", "OR", "OK", "CT", "UT", "PR", "IA", "NV", "AR", "MS", "KS", "NM", "NE", "ID", "WV", "HI", "NH", "ME", "MT", "RI", "DE", "SD", "ND", "AK", "DC", "VT", "WY"]

    #making the name more palatable
    name = namex.lower().replace(" ", "_")
    name = re.sub(r'\W+', '', name)

    #grabbing the actual values from the name it uses
    char1 = (ord(name[-2])-ord('a'))%26
    char2 = (ord(name[-1])-ord('a'))%26
    side = len(namex)%3+3

    #calculating the hues, hue1 is the background hue2 is the state
    hue1 = (0.595-(char1/26))%1
    hue2 = (14/26 - (char2/26))%1

    #This next chunk of code generates the shape that goes on the right side. i can't really tell you more because i barely understand how this works myself
    #stolen code ftw
    sider=2.3

    xy = [
        (((math.cos(th) + 1) * 100*sider)+150,
        (math.sin(th) + 1) * 70*sider)
        for th in [i * (1.75 * math.pi) / side for i in range(side)]
        ]  
    
    image = ImagePath.Path(xy).getbbox()  
    img = Image.new("RGBA",(1080,1080))

    img1 = ImageDraw.Draw(img)  
    img1.polygon(xy, fill = (0,0,0,0), outline = tuple([int(x*255) for x in colorsys.hsv_to_rgb(hue2,.596,.855)]),width=11)
    img = ImageOps.mirror(Image.Image.rotate(img,0))
    #and there's the end of the stolen code portion of this tour

    #time to fetch the assets. the bg image is just an alpha mask rn, limbs is the stuff on top and state is what it says on the tin
    state = Image.open("Helper/States/"+states[(ord(name[0])-ord('a'))%26*2+(ord(name[1])-ord('a'))%2]+".png")
    if states[(ord(name[0])-ord('a'))%26*2+(ord(name[1])-ord('a'))%2] in ["MS", "AZ", "CA", "IL", "MT", "DC"]: #thesestates have a more interesting left border than right border so i flipped them
        state = ImageOps.mirror(state)

    limbs = Image.open("Helper/Assets/book_overlay.png")
    bg = Image.open("Helper/Assets/cover_overlay.png")

    #here i'm generating a solid color image that will get masked over using bg
    colormask = Image.new('HSV', (1080, 1080), (int(hue1*255), 198, 214))
    colormask = colormask.convert("RGBA")
    bg = Image.composite(Image.new('RGBA', (1080, 1080), (0,0,0,0)), colormask, bg)
    #so now we have just the base color of the book in the book shape and nothing else! woohoo

    #this section is rescaling the state so that it'll fit properly when we put it on the book. basically just making width 1060 and keeping the aspect ration
    width = 1060
    wpercent = (width/float(state.size[0]))
    hsize = int((float(state.size[1])*float(wpercent)))
    state = state.resize((width,hsize), Image.Resampling.BILINEAR)

    #when upscaling the border gets fuzzy so i'm just setting the alpha channel to 0 or 255 for each pixel in the state
    #(and also inverting it so it functions as an alpha mask)
    A = state.getchannel('A')
    newA = A.point(lambda i: 0 if i >= 128 else 255)
    state.putalpha(newA)

    #this will come in handy later. saving now because we're about to do some more transformations yaaaay
    statesize = state.size
    
    #see line 57. basically just doing the same thing but with the other color and with the state instead of the book
    colormask = Image.new('HSV', state.size, (int(hue2*255), 201, 207))
    colormask = colormask.convert("RGBA")
    state = Image.composite(Image.new('RGBA', state.size, (0,0,0,0)), colormask, state)

    #here i'm basically moving the state so that it'll be nicely lined up and visible in the actual book. 
    #basically it's just aliging the center of the state to the center of the image and then shifting down 108 pixels
    #then i remove the excess bits so it's not hanging off the edge
    blank = Image.new('RGBA', bg.size, (0,0,0,0))
    blank.paste(state,(-170,(1080-statesize[1])//2-108),state)
    state = Image.composite(Image.new('RGBA', (1080, 1080), (0,0,0,0)), blank, Image.open("Helper/Assets/cover_overlay.png"))

    #see above but this time it's for the shape not the state
    blank = Image.new('RGBA', bg.size, (0,0,0,0))
    blank.paste(img,(60,220),img)
    img = Image.composite(Image.new('RGBA', (1080, 1080), (0,0,0,0)), blank, Image.open("Helper/Assets/cover_overlay.png"))

    #and now it's the final composition of the four images that make up the bsona
    bg = Image.alpha_composite(bg,state)
    bg = Image.alpha_composite(bg,img)
    bg = Image.alpha_composite(bg,limbs)

    #and then we save and confirm that the book has been generated
    bg.save('Helper/books/'+name+'.png',"PNG")
    return
