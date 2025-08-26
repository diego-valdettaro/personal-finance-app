import React from "react";
import { NavLink } from "react-router-dom";

type NavLinkItem = {
    to: string;
    label: string;
};

const links: NavLinkItem[] = [
    // This router is not implemented yet
    { to: "/dashboard", label: "Dashboard" },
    { to: "/management", label: "Management" },
    { to: "/transactions", label: "Transactions" },
    { to: "/expenses", label: "Expenses" },
    { to: "/debts", label: "Debts" },
    { to: "/budget", label: "Budget" },
];    

export default function Sidebar() {
    return (
        <nav className="w-52 bg-gray-100 p-4">
            <ul className="space-y-2">
                {links.map(({ to, label }) => (
                    <li key={to}>
                        <NavLink
                            to={to}
                            className={({ isActive }: { isActive: boolean }) =>
                            `block p-2 rounded hover:bg-green-200 ${isActive ? "bg-green-300" : ""}`
                            }
                        >
                            {label}
                        </NavLink>
                    </li>
                ))}
            </ul>
      </nav>
    );
}