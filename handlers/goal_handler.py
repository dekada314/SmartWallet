from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from domain.entities.goal import Goal
from keyboards import Keyboards
from use_cases.change_goal_desc_use_case import ChangeGoalDescUseCase
from use_cases.delete_goal_use_case import DeleteGoalUseCase
from use_cases.display_user_goals_use_case import DisplayUserGoals
from use_cases.exceeding_the_limit_use_case import ExceedingTheLimitUseCase
from use_cases.save_goal_use_case import SaveGoalUseCase
from use_cases.update_goal_use_case import UpdateGoalUseCase


class GoalForm(StatesGroup):
    waiting_for_goal = State()
    waiting_for_taget = State()
    waiting_for_update = State()
    waiting_for_new_desc = State()


class GoalHandler:
    def __init__(
        self,
        save_goal_us: SaveGoalUseCase,
        display_goals_us: DisplayUserGoals,
        update_goal_us: UpdateGoalUseCase,
        delete_goal_us: DeleteGoalUseCase,
        change_goal_us: ChangeGoalDescUseCase,
        exceeding_the_limits_us: ExceedingTheLimitUseCase,
    ):
        self.save_goal_us = save_goal_us
        self.display_goals_us = display_goals_us
        self.update_goal_us = update_goal_us
        self.delete_goal_us = delete_goal_us
        self.change_goal_us = change_goal_us
        self.exceeding_the_limits_us = exceeding_the_limits_us
        self.router = Router()

    def register(self):
        @self.router.message(lambda message: message.text == "Цели")
        async def handle_goaks_button(message: types.Message):
            await message.answer(
                "Выберите тип:", reply_markup=Keyboards.get_all_goals_buttons()
            )

        @self.router.callback_query(F.data == "save_goal")
        async def handle_save_goal(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            if await self.exceeding_the_limits_us.execute(callback):
                await callback.message.answer("Напишите описание вашей цели:")
                await state.set_state(GoalForm.waiting_for_goal)
            else:
                await callback.message.answer(
                    "У вас уже целых 5 целей, предлагаю пока что сфокусироваться на уже существующих"
                )

        @self.router.message(GoalForm.waiting_for_goal)
        async def handle_goal_text(message: types.Message, state: FSMContext):
            await state.update_data(goal_description=message.text)

            await message.answer("Записал!")
            await message.answer("Теперь введите сколько денег планируете копить:")
            await state.set_state(GoalForm.waiting_for_taget)

        @self.router.message(GoalForm.waiting_for_taget)
        async def handle_goal_target(message: types.Message, state: FSMContext):
            data = await state.get_data()
            goal_text = data.get("goal_description")
            await state.clear()
            goal = await self.save_goal_us.execute(message, goal_text)
            if goal:
                await message.answer("Цель успешно сохранена!")
            else:
                await message.answer("Значения введены неверно, попробуйте снова")

        @self.router.callback_query(F.data == "set_up_goal")
        async def handle_set_up_goals(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            data = await self.display_goals_us.execute(callback.from_user.id)

            await callback.message.answer("Вот все ваши цели для настройки:")

            for index, goal in enumerate(data):
                await state.update_data(goal_text=goal[0])
                await callback.message.answer(
                    f"<b>{index + 1}. {goal[0]}\n</b>"
                    f"Ваш прогресс по этой цели:\n\n{progress_bar(goal[2], goal[1])}",
                    parse_mode="HTML",
                    reply_markup=Keyboards.get_setup_goal_button(str(goal[3])),
                )

        @self.router.callback_query(F.data.startswith("del_goal_"))
        async def handle_delete_goal(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            user_goal_id = int(callback.data.split("del_goal_")[1])
            await callback.message.answer(user_goal_id)

            goal = await self.delete_goal_us.execute(callback, user_goal_id)

            if goal:
                await callback.message.answer("Цель успешно удалена")

        @self.router.callback_query(F.data.startswith("update_desc_"))
        async def handle_change_desc(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            user_goal_id = int(callback.data.split("update_desc_")[1])
            await state.update_data(user_goal_id=user_goal_id)
            await callback.message.answer("Введите новое описание цели:")
            await state.set_state(GoalForm.waiting_for_new_desc)

        @self.router.message(GoalForm.waiting_for_new_desc)
        async def change_desc(message: types.Message, state: FSMContext):
            data = await state.get_data()
            user_goal_id = data.get("user_goal_id")
            goal = await self.change_goal_us.execute(message, user_goal_id)
            if goal:
                await message.answer("Описание цели было успешно изменено!")
            await state.clear()

        def progress_bar(current, total, length=10):
            percent = current / total
            to_fill = int(percent * length)
            return "🟩" * to_fill + "⬜️" * (length - to_fill) + f"{percent * 100}%"

        @self.router.callback_query(F.data == "display_goals")
        async def handle_set_up_goals(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            data = await self.display_goals_us.execute(callback.from_user.id)

            if not data:
                await callback.message.answer("Ваш список целей пока что пуст!")
            else:
                await callback.message.answer("Вот все ваши цели:")

                for index, goal in enumerate(data):
                    await state.update_data(goal_text=goal[0])
                    await callback.message.answer(
                        f"<b>{index + 1}. {goal[0]}\n</b>"
                        f"Ваш прогресс по этой цели:\n\n{progress_bar(goal[2], goal[1])}",
                        parse_mode="HTML",
                        reply_markup=Keyboards.get_update_goal_button(str(goal[3])),
                    )

        @self.router.callback_query(F.data.startswith("update_goal_"))
        async def update_goal(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            user_goal_num = int(callback.data.split("update_goal_")[1])
            await state.update_data(goal_id=user_goal_num)
            await callback.message.answer("Введите сколько хотите внести в цель")
            await state.set_state(GoalForm.waiting_for_update)

        @self.router.message(GoalForm.waiting_for_update)
        async def handle_update_goal(message: types.Message, state: FSMContext):
            data = await state.get_data()
            goal_id = data.get("goal_id")
            goal_callback = await self.update_goal_us.execute(message, goal_id)

            if isinstance(goal_callback, Goal):
                await message.answer("Ваши накопления записаны")
            elif goal_callback == 0:
                await message.answer(
                    "Ого, как вы точно расчитали! Цель <b>идеально</b> выполнена",
                    parse_mode="HTML",
                )
            elif goal_callback > 0:
                await message.answer(
                    f"Поздравляю! Вы выполнили свою цель!!! И даже перевыполнили на {goal_callback}"
                )
            else:
                await message.answer("Кажется вы что-то не так ввели")
