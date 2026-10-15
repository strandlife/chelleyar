# ==================================================================
# ناوبری — طبق مدل مسیریابی فلت
# استک ویوهای هر مسیر: همیشه از ریشه (/) تا خودِ مسیر
# ==================================================================

NAV_STACKS = {
    "/":        ["/"],
    "/add":     ["/", "/add"],
    "/edit":    ["/", "/edit"],
    "/about":   ["/", "/about"],
    "/status":  ["/", "/status"],
    "/science": ["/", "/science"],
    "/backup":  ["/", "/backup"],
    "/stats":   ["/", "/status", "/stats"],
    "/day":     ["/", "/status", "/day"],
    "/catchup": ["/", "/status", "/catchup"],
}

# مسیرهایی که برای ساخته‌شدن به current_chelleh نیاز دارند
CHELEH_ROUTES = ("/status", "/stats", "/day", "/catchup")
DESKTOP_MIN_WIDTH = 600