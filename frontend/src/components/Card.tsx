import React from "react";

type CardProps = {
    title: string;
    value: string | number;
}

export default function Card({ title, value }: CardProps) {
    return (
        <div className="bg-white shadow rounded p-4 flex flex-col">
            <span className="text-gray-500 uppercase text-sm">{title}</span>
            <span className="text-2xl font-bold mt-2">{value}</span>
        </div>
    );
}