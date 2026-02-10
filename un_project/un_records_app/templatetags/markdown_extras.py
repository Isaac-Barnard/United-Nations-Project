import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def markdownify(text):
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Replace double newlines with a placeholder
    text = text.replace('\n\n', '|||PARAGRAPH_BREAK|||')
    
    # Replace remaining single newlines with <br>
    text = text.replace('\n', '<br>\n')
    
    # Restore paragraph breaks
    text = text.replace('|||PARAGRAPH_BREAK|||', '\n\n')
    return mark_safe(markdown.markdown(text))


@register.filter
def preview_text(text, length=200):
    """Convert markdown to plain text for Open Graph previews"""
    import re
    
    # Normalize line endings (same as markdownify)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    # Remove headers (# ## ### etc)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markers (**, *, __, _)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove strikethrough ~~text~~
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    
    # Remove inline code `code`
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove code blocks ```code```
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    
    # Remove blockquotes > 
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Remove list markers (-, *, +, 1., 2., etc)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Convert double newlines to single space (paragraph breaks)
    text = re.sub(r'\n\n+', ' ', text)
    
    # Convert single newlines to spaces
    text = text.replace('\n', ' ')
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Truncate to specified length, breaking at word boundary
    if len(text) > length:
        text = text[:length].rsplit(' ', 1)[0] + '...'
    
    return text