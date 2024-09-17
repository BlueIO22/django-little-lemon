import { RouteObject } from "react-router-dom";
import Booking from "./Booking/Booking";
import Home from "./Home/Home";
import Menu from "./Menu/Menu";
import MyPage from "./MyPage/MyPage";

export const routes = [
  {
    path: "/",
    id: "Home",
    element: <Home />,
  },
  {
    path: "/menu",
    id: "Menu",
    element: <Menu />,
  },
  {
    path: "/booking",
    id: "Booking",
    element: <Booking />,
  },
  {
    path: "/my-page",
    id: "My Page",
    element: <MyPage />,
  },
] as RouteObject[];
