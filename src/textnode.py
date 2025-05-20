#textnode.py
from enum import Enum
from htmlnode import LeafNode, ParentNode
import re

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"
    
def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return ParentNode("b", [LeafNode(None, text_node.text)])
    elif text_node.text_type == TextType.ITALIC:
        return ParentNode("i", [LeafNode(None, text_node.text)])
    elif text_node.text_type == TextType.CODE:
        return ParentNode("code", [LeafNode(None, text_node.text)])
    elif text_node.text_type == TextType.LINK:
        return ParentNode("a", [LeafNode(None, text_node.text)], {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError("Unknown text type")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT and isinstance(node, TextNode):
            parts = node.text.split(delimiter)
            if len(parts) % 2 == 0:
                raise Exception("Invalid Markdown Syntax")
            for i in range(len(parts)):
                if i % 2 == 0:
                     new_nodes.append(TextNode(parts[i], TextType.TEXT))
                else:
                    new_nodes.append(TextNode(parts[i], text_type))
                    
        else:
            new_nodes.append(node)
            
    return new_nodes

def extract_markdown_images(text):
    pattern = r"!\[(.*?)\]\((.*?)\)"
    
    return re.findall(pattern, text)

def extract_markdown_links(text):
    pattern = r"\[(.*?)\]\((.*?)\)"
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        images = extract_markdown_images(old_node.text)

        if not images:
            new_nodes.append(old_node)
            continue
        
        # Start with the original text
        remaining_text = old_node.text
        
        for alt, url in images:
            image_markdown = f"![{alt}]({url})"
            # Split only on the first occurrence
            parts = remaining_text.split(image_markdown, 1)
            
            # Add text before the image
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
                
            # Add the image node
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            
            # Update remaining_text for the next iteration
            if len(parts) > 1:
                remaining_text = parts[1]
            else:
                remaining_text = ""
                break  # No more text to process
        
        # Add any text that remains after processing all images
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
            
    return new_nodes



def split_nodes_link(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        links = extract_markdown_links(node.text)

        if not links:
            new_nodes.append(node)
            continue

        remaining_text = node.text
        for text, url in links:
            link_markdown = f"[{text}]({url})"
            parts = remaining_text.split(link_markdown, 1)
            
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))

            new_nodes.append(TextNode(text, TextType.LINK, url))
            if len(parts) > 1:
                remaining_text = parts[1]
            else:
                remaining_text = ""

            if remaining_text:
                new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    return nodes