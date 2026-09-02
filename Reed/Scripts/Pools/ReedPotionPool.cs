using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts;

/// <summary>鑻囪崏瑙掕壊鐨勪笓灞炶嵂姘存睜</summary>
public class ReedPotionPool : TypeListPotionPoolModel
{
    public override string? TextEnergyIconPath => "res://Reed/images/energy_reed.svg";
    public override string? BigEnergyIconPath => "res://Reed/images/energy_reed_big.svg";
    public override string EnergyColorName => "reed";
}

