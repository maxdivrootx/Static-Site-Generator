from enum import Enum
from htmlnode import LeafNode, ParentNode, HTMLNODE
from textnode import text_node_to_html_node, TextNode, TextType, text_to_textnodes, extract_markdown_images, extract_markdown_links

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST ="ordered_list"


def block_to_block_type(markdown):
    lines = markdown.split("\n")
    if markdown.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    elif markdown.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    elif markdown.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    elif markdown.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH



    



def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children_nodes = ParentNode("div", [])

    for block in blocks:
        # Skip empty blocks
        if not block.strip():
            continue
            
        # Determine the block type
        block_type = block_to_block_type(block)
        # Process based on block type
        if block_type == BlockType.PARAGRAPH:
            # Normalize paragraph text
            paragraph_text = ' '.join(block.split())
            p_node = ParentNode("p", text_to_children(paragraph_text))
            children_nodes.children.append(p_node)
            
        elif block_type == BlockType.HEADING:
            # Process heading (h1-h6)
            level = 0
            for char in block:
                if char == '#':
                    level += 1
                else:
                    break
            heading_text = block[level:].strip()
            h_node = ParentNode(f"h{level}", text_to_children(heading_text))
            children_nodes.children.append(h_node)

        elif block_type == BlockType.CODE:
            # Extract code content, preserving all whitespace
            lines = block.split('\n')
            
            # Check if the first line is ``` and the last line is ```
            if lines[0].strip() == '```' and lines[-1].strip() == '```':
                # Get the content between the ``` markers, preserving newlines
                code_content = '\n'.join(lines[1:-1])
                
                # Important: Add a newline at the end to match expected format
                if not code_content.endswith('\n'):
                    code_content += '\n'
            
                # Create code node without parsing inline markdown
                code_node = TextNode(code_content, TextType.TEXT)
                html_code_node = text_node_to_html_node(code_node)
                pre_node = ParentNode("pre", [ParentNode("code", [html_code_node])])
                children_nodes.children.append(pre_node)

        elif block_type == BlockType.QUOTE:
            # Process quote content by removing > markers
            quote_content = "\n".join([line.lstrip(">").strip() for line in block.split("\n")])
            children_nodes.children.append(ParentNode("blockquote", text_to_children(quote_content)))

        elif block_type == BlockType.UNORDERED_LIST:
            li_nodes = []
            for item in block.split("\n"):
                if item.strip():
                    content = item.strip()[2:].strip()
                    li_nodes.append(ParentNode("li", text_to_children(content)))
            children_nodes.children.append(ParentNode("ul", li_nodes))

        elif block_type == BlockType.ORDERED_LIST:
            li_nodes = []
            for item in block.split("\n"):
                if item.strip():
                    # Find position after first period and space
                    pos = item.find(". ")
                    if pos != -1:
                        content = item[pos+2:].strip()
                        li_nodes.append(ParentNode("li", text_to_children(content)))
            children_nodes.children.append(ParentNode("ol", li_nodes))

        

    return children_nodes


def text_to_children(text):
    # Convert text to text nodes with all inline markdown processing
    text_nodes = text_to_textnodes(text)
    
    # Convert text nodes to HTML nodes
    html_nodes = []
    for node in text_nodes:
        html_node = text_node_to_html_node(node)
        html_nodes.append(html_node)
    
    return html_nodes



def markdown_to_blocks(markdown):
    blocks = markdown.strip().split("\n\n")
    return [block.strip() for block in blocks if block.strip()]

def extract_title(markdown):
    if markdown.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return markdown.replace("#", "").strip()
    return markdown
    