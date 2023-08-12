import os
import glob
import argparse
import dominate
from dominate.tags import meta, h3, table, tr, td, p, a, img, br
from thumbs import * 
from tqdm import tqdm

class HTML:
    """This HTML class allows us to save images and write texts into a single HTML file.

     It consists of functions such as <add_header> (add a text header to the HTML file),
     <add_images> (add a row of images to the HTML file), and <save> (save the HTML to the disk).
     It is based on Python library 'dominate', a Python library for creating and manipulating HTML documents using a DOM API.
    """

    def __init__(self, web_dir, title, refresh=0):
        """Initialize the HTML classes

        Parameters:
            web_dir (str) -- a directory that stores the webpage. HTML file will be created at <web_dir>/index.html; images will be saved at <web_dir/images/
            title (str)   -- the webpage name
            refresh (int) -- how often the website refresh itself; if 0; no refreshing
        """
        self.title = title
        #self.web_dir = web_dir
        #self.img_dir = os.path.join(self.web_dir, 'images')
        #if not os.path.exists(self.web_dir):
        #   os.makedirs(self.web_dir)
        #if not os.path.exists(self.img_dir):
        #    os.makedirs(self.img_dir)

        self.doc = dominate.document(title=title)
        if refresh > 0:
            with self.doc.head:
                meta(http_equiv="refresh", content=str(refresh))

    def get_image_dir(self):
        """Return the directory that stores images"""
        return './'

    def add_header(self, text):
        """Insert a header to the HTML file

        Parameters:
            text (str) -- the header text
        """
        with self.doc:
            h3(text)

    def add_images(self, ims, txts, links, color=True, width=300):
        """add images to the HTML file
        Parameters:
            ims (str list)   -- a list of image paths
            txts (str list)  -- a list of image names shown on the website
            links (str list) --  a list of hyperref links; when you click an image, it will redirect you to a new page
        """
        if color:
            self.t = table(border=1, style="table-layout: fixed;background-color:#FFFFE0")  # Insert a table
        else:
            self.t = table(border=1, style="table-layout: fixed;")  # Insert a table
        self.doc.add(self.t)
        with self.t:
            with tr():
                for im, txt, link in zip(ims, txts, links):
                    with td(style="word-wrap: break-word; background-color:#FFFFE0", halign="center", valign="top"):
                        with p():
                            with a(href=link):
                                img(style="width:%dpx" % width, src=im)
                            br()
                            p(txt)

    def save(self):
        """save the current content to the HMTL file"""
        html_file = 'index.html'
        f = open(html_file, 'wt')
        f.write(self.doc.render())
        f.close()



if __name__ == '__main__':  # we show an example usage here.
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-o','--o', nargs='+', default=None, help='<Optinal> Set the folders to use, and make the order')
    parser.add_argument('--thumb', action='store_true') #compute the thumbnails for many very large images
    parser.add_argument('--thumb_dir', default='./thumb', type=str) #base folder to save thumb
    args = parser.parse_args()

    all_glob_folder = sorted(glob.glob('./*'))
    all_folders = [ name for name in all_glob_folder if os.path.isdir(name) and name != './thumb' and name != './__pycache__'] #ignore thumb
    all_folders = [ item[2:] for item in all_folders] #process the name to ignore ./ path

    #define result categories
    if args.o == None:
        type_list = all_folders
        type_text_list = all_folders
    else:
        type_list = args.o
        type_text_list = args.o
    
    #define file_list to extract tag for each line
    folder_to_use = type_list[0] #choose the first folder
    file_list = sorted(glob.glob(os.path.join('./', folder_to_use, '**'), recursive=True))
    file_list = [i for i in file_list if os.path.isfile(i)]
    
    if args.thumb: #use precomputed thumb for image files
        thumbnail_generators = ThumbnailGenerator(args.thumb_dir, [512,512], imscale=1, preserve_aspect=True, quality=95)
        table_file_list = []
        print('precomputing thumbnails')
        for thumbf in tqdm(file_list): #go compressing the images
            for cat in type_list:
                thumb_file_list = thumbnail_generators.make_thumb(thumbf.replace(folder_to_use, cat))
                if cat == folder_to_use:
                    table_file_list.append(thumb_file_list)
    else:
        table_file_list = file_list.copy() #copy the file_list to avoid changing it
    #Generate Table-based Html     
    html = HTML('./', 'table_html')
    html.add_header('Visualization Tools in Table')
    for ind, n in enumerate(table_file_list):
        ims = []
        links = []
        for cat in type_list:
            image_name = n.replace(folder_to_use, cat)
            ims.append(image_name)
            links.append('./toggle_index.html?tag=' + image_name.split(cat + '/')[1] + '&type=' + cat) 
        html.add_images(ims, type_text_list, links, False)
    html.save()

    

    #Generate Toggle-based Html, always use the high-res images
    #define the key to search and replace
    define_type = 'var types = ["type1","type2"]'
    change_type1 = 'if (type == "type1"){$("footer").innerHTML = "type1_text";}'
    change_type2 = 'else if (type == "type2"){$("footer").innerHTML = "type2_text";fh = 40;}'
    toggle_type1 = '<td><div id="typeText_type1" class="navunselected" onmousedown="changeType(&#39;type1&#39;);">type1_text</div></td>'
    toggle_type2 = '<td><div id="typeText_type2" class="navunselected" onmousedown="changeType(&#39;type2&#39;);">type2_text</div></td>'
    tag_ans = '<option value="1">Sample_01</option>'

    #start changing and switching
    lines = [] #lines to save the html code contents
    with open(r'comp.html', mode='r') as f:
        for line in f.readlines(): # iterate thru the lines
            if define_type in line:
                new_line = 'var types = ['
                for it, t in enumerate(type_list): #go over all the type list
                    new_line = new_line + '"' + t + '"'
                    if it != len(type_list) - 1:
                        new_line += ','
                new_line += ']\n'
                lines.append(new_line)
            elif change_type1 in line: #change type 1
                lines.append(line.replace('type1_text', type_text_list[0]).replace('type1',type_list[0]))
            elif change_type2 in line: #change type 2-k
                for it in range(len(type_list)-1):
                    lines.append(line.replace('type2_text', type_text_list[it+1]).replace('type2',type_list[it+1]))

            elif toggle_type1 in line: #toggle type 1
                lines.append(line.replace('type1_text', type_text_list[0]).replace('type1',type_list[0]))
            elif toggle_type2 in line: #toggle type 2-k
                for it in range(len(type_list)-1):
                    lines.append(line.replace('type2_text', type_text_list[it+1]).replace('type2',type_list[it+1]))

            elif tag_ans in line: # check if is in ans in line
                for f in file_list:
                    tag = f.split('/')[2]
                    for tt in f.split('/')[3:]:
                        tag = os.path.join(tag, tt) #the filename as the tag
                    new_line = '<option value="' + tag + '">' + tag + '</option>\n'
                    lines.append(new_line)
            else: 
                lines.append(line)

    #write to a new file
    with open('toggle_index.html', mode='w') as new_f:
        new_f.writelines(lines)
