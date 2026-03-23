from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from keyboards import Keyboards
from use_cases.display_user_goals_use_case import DisplayUserGoals
from use_cases.save_goal_use_case import SaveGoalUseCase
from use_cases.update_goal_use_case import UpdateGoalUseCase


class GoalForm(StatesGroup):
    waiting_for_goal = State()
    waiting_for_taget = State()
    waiting_for_update = State()


class GoalHandler:
    def __init__(
        self,
        save_goal_us: SaveGoalUseCase,
        display_goals_us: DisplayUserGoals,
        update_goal_us: UpdateGoalUseCase,
    ):
        self.save_goal_us = save_goal_us
        self.display_goals_us = display_goals_us
        self.update_goal_us = update_goal_us
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
            await callback.message.answer("Напишите описание вашей цели")
            await state.set_state(GoalForm.waiting_for_goal)

        @self.router.message(GoalForm.waiting_for_goal)
        async def handle_goal_text(message: types.Message, state: FSMContext):
            await state.update_data(goal_description=message.text)

            await message.answer("Введите сколько денег планируете копить:")
            await state.set_state(GoalForm.waiting_for_taget)

        @self.router.message(GoalForm.waiting_for_taget)
        async def handle_goal_target(message: types.Message, state: FSMContext):
            data = await state.get_data()
            goal_text = data.get("goal_description")
            await state.clear()
            await self.save_goal_us.execute(
                message.from_user.id, float(message.text), 0, goal_text
            )

        @self.router.callback_query(F.data == "del_goal")
        async def handle_del_goal(callback: CallbackQuery):
            await callback.answer()

        @self.router.callback_query(F.data == "set_up_goal")
        async def handle_set_up_goals(callback: CallbackQuery):
            await callback.answer()

        def progress_bar(current, total, length=10):
            percent = current / total
            to_fill = int(percent * length)
            return "🟩" * to_fill + "⬜️" * (length - to_fill) + f"{percent * 100}%"

        @self.router.callback_query(F.data == "display_goals")
        async def handle_set_up_goals(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            data = await self.display_goals_us.execute(callback.from_user.id)

            await callback.message.answer("Вот все ваши цели:")

            for index, goal in enumerate(data):
                await state.update_data(goal_text=goal[0])
                await callback.message.answer(
                    f"<b>{index + 1}. {goal[0]}\n</b>"
                    f"Ваш прогресс по этой цели:\n\n{progress_bar(goal[2], goal[1])}",
                    parse_mode="HTML",
                    reply_markup=Keyboards.get_update_goal_button(str(index + 1)),
                )

        @self.router.callback_query(F.data.startswith("update_goal_"))
        async def update_goal(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            user_goal_num = callback.data.split("update_goal_")[1]
            await callback.message.answer(user_goal_num)
            await state.update_data(goal_id = user_goal_num)
            await callback.message.answer("Введите сколько хотите внести в цель")
            await state.set_state(GoalForm.waiting_for_update)

        @self.router.message(GoalForm.waiting_for_update)
        async def handle_update_goal(message: types.Message, state: FSMContext):
            data = await state.get_data()
            goal_id = data.get("goal_id")
            goal_callback = await self.update_goal_us.execute(user_id=message.from_user.id, goal_id=goal_id,curr_bill=float(message.text))
            # if not goal_callback:
            #     await message.answer("Поздравляю! Вы выполнили свою цель!!!")
                
            
