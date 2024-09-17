import { matchPath, RouteObject } from "react-router-dom";
import { routes } from "../../router";

export default function Navbar() {
  function isActiveRoute(route: RouteObject) {
    return matchPath(route.path ?? "", location.pathname);
  }

  return (
    <nav className="w-full flex justify-center items-center flex-col p-10 gap-10">
      <img src="logo.png" alt="" />
      <ul className="flex justify-center gap-5 w-[800px] p-5 bg-primary rounded-lg">
        {routes.map((route: RouteObject) => {
          return (
            <li
              className={
                "text-white text-xl " + (isActiveRoute(route) && "font-bold")
              }
              key={route.id}
            >
              <a href={route.path}>{route.id}</a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
