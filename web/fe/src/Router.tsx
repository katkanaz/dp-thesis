import { createRootRoute, createRoute, createRouter, Outlet } from "@tanstack/react-router";
import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import Results from "./pages/Results";
import ResultDetail from "./pages/ResultDetail";
import Docs from "./pages/Docs";
import Stats from "./pages/Stats";

const rootRoute = createRootRoute({
    component: () => (
        <>
            <NavBar />
            <Outlet />
        </>
    ),
})

export const homeRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/",
    component: Home,
})

export const resultsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/results",
    component: Results,
})

export const resultDetailRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/results/$afId",
    component: ResultDetail,
})

export const statsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/stats",
    component: Stats,
})

export const docsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/docs",
    component: Docs,
})

const routeTree = rootRoute.addChildren([homeRoute, resultsRoute, resultDetailRoute, docsRoute, statsRoute])

export const router = createRouter({ routeTree })
