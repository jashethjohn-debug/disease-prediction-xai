import { useState } from "react";

export const useApiState = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const withLoader = async (fn) => {
    setLoading(true);
    setError("");
    try {
      return await fn();
    } catch (err) {
      setError(err?.response?.data?.error || "Something went wrong");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, withLoader, setError };
};
