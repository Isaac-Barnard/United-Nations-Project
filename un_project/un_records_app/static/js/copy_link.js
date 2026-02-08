function copyResolutionLink(url, button) {
    console.log('Attempting to copy URL:', url);
    
    if (!navigator.clipboard) {
        console.error('Clipboard API not available');
        alert('Clipboard API not supported in this context');
        return;
    }
    
    navigator.clipboard.writeText(url).then(() => {
        console.log('Successfully copied!');
        const original = button.textContent;
        button.textContent = '✓';
        button.classList.add('copied');

        setTimeout(() => {
            button.textContent = original;
            button.classList.remove('copied');
        }, 1200);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy: ' + err.message);
    });
}