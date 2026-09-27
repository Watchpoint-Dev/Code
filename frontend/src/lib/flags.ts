const countryCodeMap: Record<string, string> = {
  USA: "US",
  CH: "CH",
  UK: "GB",
  FR: "FR",
  DE: "DE",
  AE: "AE",
  IT: "IT",
  CA: "CA",
  JP: "JP",
  ES: "ES",
  HK: "HK",
};

export const getFlagEmoji = (location: string) => {
  const lastToken = location.split(",").pop()?.trim() ?? "";
  const code = countryCodeMap[lastToken] ?? lastToken;
  if (!/^[A-Z]{2}$/.test(code)) return "🏳️";
  return String.fromCodePoint(...[...code].map((char) => 127397 + char.charCodeAt(0)));
};
