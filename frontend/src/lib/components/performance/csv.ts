export function downloadCsv(filename: string, rows: Record<string, unknown>[]): void {
    const data = rows.length > 0 ? rows : [{ message: 'No data' }];
    const headers = Object.keys(data[0]);
    const escape = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const lines = [
        headers.map(escape).join(','),
        ...data.map((row) => headers.map((h) => escape(row[h])).join(',')),
    ];
    const blob = new Blob([lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
