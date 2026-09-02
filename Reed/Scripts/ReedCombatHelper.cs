using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts;

/// <summary>
/// 战斗辅助工具：获取敌人列表、查询能力层数、手牌操作、治疗等。
/// API 已通过 mod 源码验证（AutoPlayMod、snakebite-enhance、RitsuLibModTemplate）。
/// </summary>
internal static class ReedCombatHelper
{
    /// <summary>
    /// 获取某生物所在战斗中所有敌方生物（返回快照，可在 foreach+await 中安全使用）。
    /// 使用 Enemies（而非 HittableEnemies）以包含分裂怪物/minion 等次要敌人。
    /// </summary>
    public static IEnumerable<Creature> GetEnemies(Creature creature)
    {
        return creature.CombatState?.Enemies.ToList() ?? (IEnumerable<Creature>)[];
    }

    /// <summary>
    /// 获取玩家所在战斗中所有敌方生物（返回快照）。
    /// </summary>
    public static IEnumerable<Creature> GetEnemies(Player player)
    {
        return player.Creature.CombatState?.Enemies.ToList() ?? (IEnumerable<Creature>)[];
    }

    /// <summary>
    /// 检查某生物是否拥有指定能力。
    /// 已确认 API: creature.HasPower&lt;T&gt;()
    /// </summary>
    public static bool HasPower<TPower>(Creature creature) where TPower : ModPowerTemplate
    {
        return creature.HasPower<TPower>();
    }

    /// <summary>
    /// 获取某生物身上某能力的层数。
    /// 已确认 API: creature.GetPowerAmount&lt;T&gt;()
    /// </summary>
    public static int GetPowerAmount<TPower>(Creature creature) where TPower : ModPowerTemplate
    {
        return creature.GetPowerAmount<TPower>();
    }

    /// <summary>
    /// 获取玩家手牌中的所有卡牌。
    /// 已确认 API: PileType.Hand.GetPile(player).Cards 返回 List&lt;CardModel&gt;
    /// </summary>
    public static IEnumerable<CardModel> GetHandCards(Player player)
    {
        return PileType.Hand.GetPile(player).Cards;
    }

    /// <summary>
    /// 消耗一张手牌。
    /// 最佳猜测 API: CardCmd.Exhaust(choiceContext, card)
    /// TODO: 编译时验证确切签名。
    /// </summary>
    public static async Task ExhaustCard(CardModel card, PlayerChoiceContext choiceContext)
    {
        await CardCmd.Exhaust(choiceContext, card);
    }

    /// <summary>
    /// 创建一张指定类型的卡牌并加入手牌。
    /// 已确认 API: combatState.CreateCard&lt;T&gt;(player) + CardPileCmd.AddGeneratedCardsToCombat
    /// </summary>
    public static async Task AddCardToHand<TCard>(PlayerChoiceContext choiceContext, Player player)
        where TCard : ModCardTemplate, new()
    {
        var card = player.Creature.CombatState.CreateCard<TCard>(player);
        await CardPileCmd.AddGeneratedCardsToCombat([card], PileType.Hand, player, CardPilePosition.Top);
    }

    /// <summary>
    /// 治疗目标。
    /// 最佳猜测 API: CreatureCmd.Heal(choiceContext, target, amount)
    /// TODO: 编译时验证确切签名。
    /// </summary>
    public static async Task Heal(Creature target, int amount, PlayerChoiceContext choiceContext)
    {
        await CreatureCmd.Heal(target, (decimal)amount, true);
    }

    /// <summary>
    /// 移除目标身上所有指定能力的层数。
    /// 通过施加负值来减少层数（参考传炬 PassingTheTorch 的实现方式）。
    /// </summary>
    public static async Task RemoveAllPower<TPower>(Creature target, PlayerChoiceContext choiceContext)
        where TPower : ModPowerTemplate
    {
        int amount = GetPowerAmount<TPower>(target);
        if (amount > 0)
        {
            await PowerCmd.Apply<TPower>(choiceContext, target, -amount, target, null);
        }
    }

    /// <summary>
    /// 获取某生物所在战斗中所有友方生物（含自身，返回快照）。
    /// 联机模式中包含其他玩家。
    /// </summary>
    public static IEnumerable<Creature> GetAllies(Creature creature)
    {
        return creature.CombatState?.Allies.ToList() ?? (IEnumerable<Creature>)[];
    }

    /// <summary>
    /// 获取某生物所在战斗中所有友方生物（不含自身，返回快照）。
    /// 联机模式中包含其他玩家。
    /// </summary>
    public static IEnumerable<Creature> GetOtherAllies(Creature creature)
    {
        return GetAllies(creature).Where(a => a != creature).ToList();
    }

    /// <summary>
    /// 获取所有敌人身上指定能力的层数总和。
    /// </summary>
    public static int GetAllEnemiesPowerTotal<TPower>(Creature creature) where TPower : ModPowerTemplate
    {
        int total = 0;
        foreach (var enemy in GetEnemies(creature))
        {
            total += GetPowerAmount<TPower>(enemy);
        }
        return total;
    }
}
