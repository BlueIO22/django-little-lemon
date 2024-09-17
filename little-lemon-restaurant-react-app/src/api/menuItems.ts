export async function getMenuItems() {
  const response = await fetch("http://localhost:8000/api/menu-items", {
    method: "GET",
    headers: {
      contentType: "application/json",
    },
  });
  console.log(response);
}
