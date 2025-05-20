from textnode import TextNode, TextType
import os
import sys
import shutil
from blockmarkdown import markdown_to_html_node, extract_title

def main():
    text_type = TextNode("This is some anchor text", "Links", "https://www.boot.dev")
    print(text_type)
    source = "static"
    destination = "docs"
    if os.path.exists(destination):
        shutil.rmtree(destination)
    copy_to_destination_dir(source, destination)
    template_path = "template.html"
    from_path = "content"
    dest_path = "docs"
    basepath = "/" 
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    generate_pages_recursively(from_path, template_path, dest_path, basepath)

    



def copy_to_destination_dir(source, destination):
    os.makedirs(destination, exist_ok=True)
    
    
    
    source_files = os.listdir(source)
    for file in source_files:
        source_file_path = os.path.join(source, file)
        destination_file_path = os.path.join(destination, file)
        
        if os.path.isfile(source_file_path):
            shutil.copy(source_file_path, destination_file_path)
        elif os.path.isdir(source_file_path):
            copy_to_destination_dir(source_file_path, destination_file_path)

def generate_page(from_path, template_path, dest_path, basepath):
    if not os.path.exists(dest_path):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(from_path) as f:
        path_content = f.read()
    with open(template_path) as f:
        template_content = f.read()
    # Convert markdown to HTML
    html_string = markdown_to_html_node(path_content).to_html()
    title = extract_title(path_content)
    new_content_title = template_content.replace("{{ Content }}", html_string).replace("{{ Title }}", title)
    new_content_title = new_content_title.replace('href="/', f'href="{basepath}')
    new_content_title = new_content_title.replace('src="/', f'src="{basepath}')


    with open(dest_path, "w") as f:
        f.write(new_content_title)

def generate_pages_recursively(dir_path_content, template_path, dest_dir_path, basepath):
    
    
    for files in os.listdir(dir_path_content):
        full_path = os.path.join(dir_path_content, files)
        if os.path.isfile(full_path):
            relative_path = os.path.relpath(full_path, dir_path_content)
            dest_file_path = os.path.join(dest_dir_path, relative_path.replace(".md", ".html"))
                
            # Make sure the destination directory exists
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
            if full_path.endswith(".md"):
                generate_page(full_path, template_path, dest_file_path, basepath)

        elif os.path.isdir(full_path):
            sub_dest_dir = os.path.join(dest_dir_path, files)
            os.makedirs(sub_dest_dir, exist_ok=True)
            generate_pages_recursively(full_path, template_path, sub_dest_dir, basepath)

if __name__ == "__main__":
    main()