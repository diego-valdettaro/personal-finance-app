import React from "react";
import Sidebar from "./Sidebar";
import { Outlet } from "react-router-dom";

export default function Layout() {
    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-6 overflow-auto">
                <Outlet />
            </main>
        </div>
    );
}