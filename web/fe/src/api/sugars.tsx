export type Sugar = {
    name: string;
    abrev: string;
    img: string;
};

export const getSugars = async (): Promise<Sugar[]> => {
    const res = await fetch("/api/sugars");
    if (!res.ok) throw new Error("Failed to fetch sugars");
    const data: Sugar[] = await res.json();
    return data;
};
