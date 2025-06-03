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