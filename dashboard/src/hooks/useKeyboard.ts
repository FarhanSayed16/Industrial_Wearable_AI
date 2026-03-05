import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function useKeyboard() {
    const navigate = useNavigate();

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Only trigger on Ctrl or Cmd
            if (!e.ctrlKey && !e.metaKey) return;

            switch (e.key) {
                case "1":
                    e.preventDefault();
                    navigate("/");
                    break;
                case "2":
                    e.preventDefault();
                    navigate("/sessions");
                    break;
                case "3":
                    e.preventDefault();
                    navigate("/analytics");
                    break;
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [navigate]);
}
