import logoUrl from "../assets/pipelens-logo.svg";

export function PipeLensLogo({ size = 40 }: { size?: number }) {
  return (
    <img src={logoUrl} alt="PipeLens" width={size} height={size} style={{ display: "block" }} />
  );
}
