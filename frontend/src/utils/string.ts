export function toProperCase(str: string) {
    return str
        .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) =>
            index === 0 ? word.toUpperCase() : word.toLowerCase()
        )
        .replace(/\s+/g, '');
}