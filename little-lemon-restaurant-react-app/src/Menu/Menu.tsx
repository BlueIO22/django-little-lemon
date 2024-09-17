import { useEffect } from "react";
import { getMenuItems } from "../api/menuItems";

export default function Menu() {
  useEffect(() => {
    getMenuItems().then((data) => {});
  }, []);
  return <></>;
}
