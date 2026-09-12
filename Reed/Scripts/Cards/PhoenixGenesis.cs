using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Character;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Cards;

/// <summary>
/// 凤焰新生（Phoenix Genesis）——苇草的第二张先古卡。
/// 通过达弗的薄污之书获得。
/// 2费技能牌，消耗。
/// 消耗所有灰烬，每层灰烬回复 {Cards} 点生命并对所有敌人施加 2 层灼燃，获得 1 点力量。
/// 升级后费用减一（2费→1费）。
/// </summary>
[RegisterDustyTomeCard(typeof(ReedCharacter))]
public sealed class PhoenixGenesis : ModCardTemplate
{
    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = false;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    public override CardVisualStyle CustomVisualStyle => CardVisualStyle.Ancient;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(3) // 每层灰烬回复的生命值
    ];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public PhoenixGenesis() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int ashStacks = ReedCombatHelper.GetPowerAmount<Ash>(Owner.Creature);

        if (ashStacks > 0)
        {
            // 消耗所有灰烬
            await ReedCombatHelper.RemoveAllPower<Ash>(Owner.Creature, choiceContext);

            // 每层灰烬回复生命
            await ReedCombatHelper.Heal(
                Owner.Creature,
                ashStacks * DynamicVars.Cards.IntValue,
                choiceContext);

            // 每层灰烬对所有敌人施加 2 层灼燃
            var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
            foreach (var enemy in enemies)
            {
                await PowerCmd.Apply<Scorch>(choiceContext, enemy, ashStacks * 2, Owner.Creature, this);
            }
        }

        // 获得 1 点力量
        await PowerCmd.Apply<StrengthPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }
}
