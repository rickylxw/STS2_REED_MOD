using Godot;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Utils;

namespace Reed.Scripts;

/// <summary>
/// Reed character's dedicated card pool. Theme color is orange-red, representing flame.
/// </summary>
public class ReedCardPool : TypeListCardPoolModel
{
    public override string Title => "reed";
    public override string EnergyColorName => "reed";

    // Energy icon used in descriptions (14x24)
    public override string? TextEnergyIconPath => "res://Reed/images/energy_reed.svg";
    // Energy icon in card top-left corner (74x74)
    public override string? BigEnergyIconPath => "res://Reed/images/energy_reed_big.svg";

    // Card pool theme color: orange-red
    public override Color DeckEntryCardColor => new(0.90f, 0.35f, 0.10f);
    // Energy panel text outline color
    public override Color EnergyOutlineColor => new(1.0f, 0.55f, 0.15f);

    // Use original card frame, recolored to orange-red via hue replacement shader
    private static readonly Material? _poolFrameMaterial =
        MaterialUtils.CreateReplaceHueShaderMaterial(0.90f, 0.35f, 0.10f);

    public override Material? PoolFrameMaterial => _poolFrameMaterial;

    public override bool IsColorless => false;
}
