"""
Simple Yargitay API Client
Direct connection to https://karararama.yargitay.gov.tr
"""
import httpx
import asyncio
from typing import Optional, List, Dict, Any


class SimpleYargitayClient:
    """Basit Yargıtay API Client - Gerçek veri çeker"""

    BASE_URL = "https://karararama.yargitay.gov.tr"
    SEARCH_ENDPOINT = "/aramadetaylist"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def search(
        self,
        query: str,
        chamber: str = "",
        date_from: str = "",
        date_to: str = "",
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Yargıtay'da arama yap

        Args:
            query: Arama kelimesi (örn: "iş hukuku")
            chamber: Daire seçimi (boş = tümü)
            date_from: Başlangıç tarihi (DD.MM.YYYY)
            date_to: Bitiş tarihi (DD.MM.YYYY)
            page: Sayfa numarası
            page_size: Sayfa başına sonuç

        Returns:
            Dict with search results
        """

        # Request payload
        payload = {
            "data": {
                "arananKelime": query,
                "birimYrgKurulDaire": chamber,
                "baslangicTarihi": date_from,
                "bitisTarihi": date_to,
                "siralama": "3",
                "siralamaDirection": "desc",
                "pageSize": page_size,
                "pageNumber": page
            }
        }

        # Headers (kritik!)
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "X-KL-KIS-Ajax-Request": "Ajax_Request",
            "Referer": f"{self.BASE_URL}/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.BASE_URL}{self.SEARCH_ENDPOINT}",
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()
                data = response.json()

                # Parse response
                if data and isinstance(data, dict):
                    results = data.get("data", {}).get("data", [])
                    total = data.get("data", {}).get("recordsTotal", 0)

                    return {
                        "success": True,
                        "query": query,
                        "total": total,
                        "page": page,
                        "page_size": page_size,
                        "results": [
                            {
                                "id": r.get("id"),
                                "daire": r.get("daire"),
                                "esas_no": r.get("esasNo"),
                                "karar_no": r.get("kararNo"),
                                "karar_tarihi": r.get("kararTarihi"),
                                "document_url": f"{self.BASE_URL}/getDokuman?id={r.get('id')}"
                            }
                            for r in results
                        ],
                        "source": "Yargıtay Official API",
                        "api_status": "real_data"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Invalid response format",
                        "api_status": "error"
                    }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout - Yargıtay API yanıt vermedi",
                "api_status": "timeout"
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                "api_status": "http_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "api_status": "error"
            }


# Test function
async def test_yargitay():
    """Test the Yargitay client"""
    client = SimpleYargitayClient()

    print("🔍 Testing Yargıtay API with 'iş hukuku'...")
    result = await client.search(
        query="iş hukuku",
        page_size=3
    )

    print(f"\n✅ Success: {result.get('success')}")
    print(f"📊 Total results: {result.get('total', 0)}")
    print(f"🔧 API Status: {result.get('api_status')}")

    if result.get('success'):
        print(f"\n📄 First {len(result.get('results', []))} results:")
        for idx, case in enumerate(result.get('results', []), 1):
            print(f"\n{idx}. {case.get('daire')}")
            print(f"   Esas No: {case.get('esas_no')}")
            print(f"   Karar No: {case.get('karar_no')}")
            print(f"   Tarih: {case.get('karar_tarihi')}")
    else:
        print(f"\n❌ Error: {result.get('error')}")

    return result


if __name__ == "__main__":
    # Run test
    asyncio.run(test_yargitay())
