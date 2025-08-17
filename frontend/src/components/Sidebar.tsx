import React from "react";
import { NavLink } from "react-router-dom";

type NavLinkItem = {
    to: string;
    label: string;
};

const links: NavLinkItem[] = [
    // This router is not implemented yet
    { to: "/dashboard", label: "Dashboard" },
    { to: "/accounts", label: "Accounts" },
    { to: "/categories", label: "Categories" },
    { to: "/people", label: "People" },
    { to: "/transactions", label: "Transactions" },
    { to: "/budgets", label: "Budgets" },
    { to: "/reports", label: "Reports" },
];    

export default function Sidebar() {
    return (
        <nav className="w-64 bg-gray-100 p-4">
            <ul className="space-y-2">
                {links.map(({ to, label }) => (
                    <li key={to}>
                        <NavLink
                            to={to}
                            className={({ isActive }: { isActive: boolean }) =>
                            `block p-2 rounded hover:bg-blue-200 ${isActive ? "bg-blue-300" : ""}`
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