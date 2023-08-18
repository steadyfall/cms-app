export const ForeignKeyTomSelectConfig = (placeholder, remove_title, allOptions) => {
    return {
        plugins: {
            'remove_button': {
                title: remove_title,
            },
            'no_backspace_delete': {},
        },
        maxItems: 1,
        items: allOptions,
        maxOptions: 10,
        openOnFocus: false,
        placeholder: placeholder,
        create: false,
        highlight: true
    }
};