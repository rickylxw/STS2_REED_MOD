using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts;

/// <summary>鑻囪崏瑙掕壊鐨勪笓灞為仐鐗╂睜</summary>
public class ReedRelicPool : TypeListRelicPoolModel
{
    public override string? TextEnergyIconPath => "res://Reed/images/energy_reed.svg";
    public override string? BigEnergyIconPath => "res://Reed/images/energy_reed_big.svg";
    public override string EnergyColorName => "reed";
}

