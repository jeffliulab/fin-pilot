import { redirect } from "next/navigation";

/**
 * 根路径默认跳转到个股模块（v0.1 唯一完整功能）.
 */
export default function Home() {
  redirect("/stock");
}
