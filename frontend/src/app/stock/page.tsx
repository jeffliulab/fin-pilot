/**
 * /stock —— 个股分析模块入口页.
 *
 * 上方：TickerInput；下方：CompanyView（按 store status 切分支渲染）.
 */

import { CompanyView } from "@/features/stock/CompanyView";
import { TickerInput } from "@/features/stock/TickerInput";

export default function StockPage() {
  return (
    <div className="flex h-full flex-col gap-4 px-6 py-5">
      <TickerInput />
      <div className="flex-1 overflow-y-auto">
        <CompanyView />
      </div>
    </div>
  );
}
